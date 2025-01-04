from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_settings

settings = get_settings()

# DB 접속 정보
SQLALCHEMY_DATABASE_URL = (
    "mysql+mysqldb://"
    f"{settings.database_username}:{settings.database_password}"
    "@127.0.0.1/fastapi-ca"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL) # DB 커넥션 풀 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # DB 접속을 위한 클래스

Base = declarative_base() # ORM 클래스의 상위 클래스