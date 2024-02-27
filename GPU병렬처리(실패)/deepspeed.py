import os
import json
import deepspeed
import torch
import torch.distributed as dist
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.utils.data.distributed import DistributedSampler
import torch.multiprocessing as mp

def save_checkpoint(model, optimizer, epoch, path):
    if dist.get_rank() == 0:
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict()
        }, path)

def load_checkpoint(model, optimizer, path):
    checkpoint = torch.load(path, map_location=lambda storage, loc: storage.cuda(dist.get_rank()))
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch']

def train_model(rank, world_size):
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

    model = AutoModelForCausalLM.from_pretrained("beomi/llama-2-ko-7b")
    tokenizer = AutoTokenizer.from_pretrained("beomi/llama-2-ko-7b", trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = model.to(rank)
    model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[rank])

    dataset = load_dataset("hyokwan/hkcode_korea", split="train")
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)

    # 배치 크기 및 그래디언트 축적 단계 조정
    batch_size = 2  # 배치 크기 줄임
    gradient_accumulation_steps = 8  # 그래디언트 축적 단계 증가

    # DeepSpeed 초기화
    model_engine, optimizer, _, _ = deepspeed.initialize(
        model=model,
        model_parameters=model.parameters(),
        config='ds_config.json'
    )

    # 데이터 로더 설정
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, sampler=sampler)

    # 체크포인트 로드 로직
    start_epoch = 0
    checkpoint_path = './checkpoint.pth'
    if os.path.exists(checkpoint_path):
        start_epoch = load_checkpoint(model, optimizer, checkpoint_path)

    # 학습 루프
    for epoch in range(start_epoch, 5):  # 5는 전체 에포크 수
        sampler.set_epoch(epoch)
        for step, batch in enumerate(dataloader):
            inputs = tokenizer(batch['text'], return_tensors='pt', padding=True, truncation=True)
            inputs = {k: v.to(rank) for k, v in inputs.items()}
            outputs = model_engine(**inputs)
            loss = outputs.loss
            model_engine.backward(loss)
            if (step + 1) % gradient_accumulation_steps == 0:
                model_engine.step()
                model_engine.zero_grad()

    dist.destroy_process_group()

def main():
    world_size = torch.cuda.device_count()
    os.environ['MASTER_ADDR'] = '172.17.0.8'
    os.environ['MASTER_PORT'] = '12345'
    mp.spawn(train_model, args=(world_size,), nprocs=world_size, join=True)

if __name__ == "__main__":
    main()
