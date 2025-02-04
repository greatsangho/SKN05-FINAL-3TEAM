# Python 3.11-slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /code

# curl 설치 (추가)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 의존성 설치
COPY ./app/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 전체 코드 복사
COPY ./app /code

# FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]