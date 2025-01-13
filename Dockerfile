# Python 3.11-slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /code

# requirements.txt 복사 및 의존성 설치
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 전체 코드 복사
COPY . /code
COPY .env /code/.env

# 기본 명령어 설정 (테스트 단계에서는 사용하지 않음)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
