import os
import subprocess

# 필요한 패키지 설치
subprocess.run(['pip', 'install', '-U', 'autotrain-advanced'])

# autotrain 설정 실행
subprocess.run(['autotrain', 'setup', '--colab'])

# 프로젝트 설정
project_name = 'sseungtest1'
model_name = 'squarelike/llama2-ko-medical-7b'

# 하이퍼파라미터 설정
learning_rate = 2e-4
num_epochs = 1
batch_size = 1
block_size = 1024
warmup_ratio = 0.1
weight_decay = 0.01
gradient_accumulation = 4
mixed_precision = 'fp16'
peft = True
quantization = 'int4'
lora_r = 16
lora_alpha = 16
lora_dropout = 0.05

# 환경 변수 설정
os.environ['PROJECT_NAME'] = project_name
os.environ['MODEL_NAME'] = model_name
os.environ['LEARNING_RATE'] = str(learning_rate)
os.environ['NUM_EPOCHS'] = str(num_epochs)
os.environ['BATCH_SIZE'] = str(batch_size)
os.environ['BLOCK_SIZE'] = str(block_size)
os.environ['WARMUP_RATIO'] = str(warmup_ratio)
os.environ['WEIGHT_DECAY'] = str(weight_decay)
os.environ['GRADIENT_ACCUMULATION'] = str(gradient_accumulation)
os.environ['MIXED_PRECISION'] = mixed_precision
os.environ['PEFT'] = str(peft)
os.environ['QUANTIZATION'] = quantization
os.environ['LORA_R'] = str(lora_r)
os.environ['LORA_ALPHA'] = str(lora_alpha)
os.environ['LORA_DROPOUT'] = str(lora_dropout)

# autotrain을 사용하여 모델 학습 실행
autotrain_command = [
    'autotrain', 'llm', '--train', '--model', '${MODEL_NAME}',
    '--project-name', '${PROJECT_NAME}', '--data-path', 'ssuengpp/test1',
    '--text-column', 'text', '--lr', '${LEARNING_RATE}', '--batch-size',
    '${BATCH_SIZE}', '--epochs', '${NUM_EPOCHS}', '--block-size',
    '${BLOCK_SIZE}', '--warmup-ratio', '${WARMUP_RATIO}', '--lora-r',
    '${LORA_R}', '--lora-alpha', '${LORA_ALPHA}', '--lora-dropout',
    '${LORA_DROPOUT}', '--weight-decay', '${WEIGHT_DECAY}',
    '--gradient-accumulation', '${GRADIENT_ACCUMULATION}',
    '--quantization', '${QUANTIZATION}', '--mixed-precision',
    '${MIXED_PRECISION}', '$([[ "$PEFT" == "True" ]] && echo "--peft")'
]

subprocess.run(autotrain_command, shell=True)
