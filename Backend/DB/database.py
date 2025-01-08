# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from config import get_settings

# settings = get_settings()

# # DB 접속 정보
# SQLALCHEMY_DATABASE_URL = (
#     "mysql+mysqldb://"
#     f"{settings.database_username}:{settings.database_password}"
#     "@127.0.0.1/fastapi-ca"
# )

# engine = create_engine(SQLALCHEMY_DATABASE_URL) # DB 커넥션 풀 생성
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # DB 접속을 위한 클래스

# Base = declarative_base() # ORM 클래스의 상위 클래스``

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경 변수가 설정되지 않았습니다.")
# print(f"Using DATABASE_URL: {DATABASE_URL}")

# -------------------
# 데이터베이스 설정
# -------------------
# DATABASE_URL = "mysql+pymysql://<USER>:<PASSWORD>@<RDS_ENDPOINT>:3306/<DATABASE_NAME>"
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()