import os
import torch
import torch.distributed as dist
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, logging
from peft import LoraConfig
from trl import SFTTrainer
from torch.utils.data.distributed import DistributedSampler
from torch.nn.parallel import DistributedDataParallel as DDP
import torch.multiprocessing as mp

def save_checkpoint(model, optimizer, epoch, path):
    if dist.get_rank() == 0:  # 체크포인트는 하나의 프로세스에서만 저장
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.module.state_dict(),  # DDP 모델의 경우 .module 사용
            'optimizer_state_dict': optimizer.state_dict()
        }, path)

def load_checkpoint(model, optimizer, path):
    checkpoint = torch.load(path, map_location=lambda storage, loc: storage.cuda(dist.get_rank()))
    model.module.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch']

def train_model(rank, world_size):
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

    model = AutoModelForCausalLM.from_pretrained("beomi/llama-2-ko-7b")
    tokenizer = AutoTokenizer.from_pretrained("beomi/llama-2-ko-7b", trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    model = DDP(model.to(rank), device_ids=[rank])

    dataset = load_dataset("hyokwan/hkcode_korea", split="train")
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)

    peft_params = LoraConfig(
        lora_alpha=16,
        lora_dropout=0.1,
        r=64,
        bias="none",
        task_type="CAUSAL_LM",
    )

    training_params = TrainingArguments(
        output_dir="./results",
        num_train_epochs=5,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        optim="paged_adamw_32bit",
        save_steps=25,
        logging_steps=25,
        learning_rate=2e-4,
        weight_decay=0.001,
        fp16=True,
        bf16=False,
        max_grad_norm=0.3,
        max_steps=-1,
        warmup_ratio=0.03,
        group_by_length=True,
        lr_scheduler_type="constant",
        report_to="tensorboard"
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_params,
        dataset_text_field="text",
        max_seq_length=None,
        tokenizer=tokenizer,
        args=training_params,
        packing=False,
        data_collator=None,
        sampler=sampler
    )

    # 체크포인트 로드 로직
    start_epoch = 0
    checkpoint_path = './checkpoint.pth'
    if os.path.exists(checkpoint_path):
        start_epoch = load_checkpoint(model, trainer.optimizer, checkpoint_path)

    for epoch in range(start_epoch, training_params.num_train_epochs):
        sampler.set_epoch(epoch)
        trainer.train()
        save_checkpoint(model, trainer.optimizer, epoch, checkpoint_path)

    dist.destroy_process_group()

def main():
    world_size = torch.cuda.device_count()
    print(world_size)
    os.environ['MASTER_ADDR'] = '172.17.0.8'
    os.environ['MASTER_PORT'] = '12355'
    mp.spawn(train_model, args=(world_size,), nprocs=world_size, join=True)

if __name__ == "__main__":
    main()
