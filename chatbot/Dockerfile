# Base 이미지
FROM python:3.11-slim as builder
# 작업 디렉토리 설정
WORKDIR /usr/src/app

# 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# 의존성 파일 복사 및 설치
COPY requirements.txt /usr/src/app/
RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt

# 프로젝트 파일 복사
COPY . /usr/src/app 

# 애플리케이션 빌드
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Gunicorn 실행
CMD ["gunicorn", "chatbot.wsgi:application", "--bind", "0.0.0.0:8000"]