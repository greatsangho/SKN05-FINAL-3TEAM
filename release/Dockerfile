# Python 3.11-slim 이미지 사용
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY ./finpilot_api_server /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# curl 설치
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

# FastAPI 실행
CMD ["gunicorn", "main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-","-c", "gunicorn_conf.py"]