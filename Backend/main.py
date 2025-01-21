from fastapi import FastAPI, Depends, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from DB import models, schemas, crud
from DB.database import engine, SessionLocal
from DB.models import Base
from datetime import datetime, timezone
from dotenv import load_dotenv
from Runpod.runpod import send_to_runpod
import uvicorn
import requests
import os

from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from Middleware.mid import TimingMiddleware, RateLimitMiddleware

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# CORS configuration (adjust as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production security
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Performance and monitoring middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TimingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# url/docs 로 기능 설명 페이지 안내
@app.get("/")
async def hello():
    return {"hello": "/docs for more info"}

# -------------------
# 데이터베이스 의존성
# -------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------
# 유저 정보 CRUD 엔드포인트
# -------------------
@app.post("/users/", response_model=schemas.Member)
def create_or_update_user(user: schemas.MemberCreate, db: Session = Depends(get_db)):
    # 현재 시간을 UTC로 설정
    current_time = datetime.now(timezone.utc)

    # 기존 유저 확인
    existing_user = crud.get_user_by_email(db=db, user_email=user.user_email)
    if existing_user:
        # 기존 유저 업데이트
        existing_user.login_time = current_time  # Update login time directly
        db.commit()
        db.refresh(existing_user)
        return existing_user

    # 새로운 유저 생성
    new_user = crud.create_user(db=db, user_email=user.user_email)
    return new_user


@app.get("/users/", response_model=list[schemas.Member])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db=db, skip=skip, limit=limit)

@app.get("/users/{user_email}", response_model=schemas.Member)
def read_user(user_email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db=db, user_email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_email}")
def delete_user(user_email: str, db: Session = Depends(get_db)):
    result = crud.delete_user(db=db, user_email=user_email)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# -------------------
# 질문 기록 CRUD 엔드포인트 및 RunPod 연동
# -------------------
@app.post("/qnas/", response_model=schemas.QnA)
def create_qna(qna: schemas.QnACreate, db: Session = Depends(get_db)):
    try:
        # RunPod 호출 (외부 서비스 연동)
        answer = send_to_runpod(qna.question)  
        
        # QnA 데이터 생성 및 저장 (session_id 자동 생성)
        new_qna = crud.create_qna(
            db=db,
            user_email=qna.user_email,
            docs_id=qna.docs_id,
            question=qna.question,
        )
        
        # 답변 추가 (RunPod 결과)
        new_qna.answer = answer
        db.commit()
        db.refresh(new_qna)

        return new_qna
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/qnas/", response_model=list[schemas.QnA])
def read_qnas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_qnas(db=db, skip=skip, limit=limit)

@app.delete("/qnas/{session_id}")
def delete_qna(session_id: str, db: Session = Depends(get_db)):
    success = crud.delete_qna(db=db, session_id=session_id)
    if not success:
        raise HTTPException(status_code=404, detail="QnA not found")
    return {"message": "QnA deleted successfully"}

# -------------------
# PDF 파일 CRUD 엔드포인트
# -------------------
@app.post("/pdfs/", response_model=schemas.PDFFile)
def create_pdf(pdf_file_data: schemas.PDFFileCreate, db: Session = Depends(get_db)):
    new_pdf_file = crud.create_pdf_file(
        db=db,
        user_email=pdf_file_data.user_email,
        docs_id=pdf_file_data.docs_id,
        file_name=pdf_file_data.file_name,
        file_time=datetime.now(timezone.utc)  # UTC 시간 설정
    )
    return new_pdf_file

@app.get("/pdfs/", response_model=list[schemas.PDFFile])
def read_pdfs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_pdfs(db=db, skip=skip, limit=limit)

@app.delete("/pdfs/{user_email}/{docs_id}")
def delete_pdf(user_email: str, docs_id: str, db: Session = Depends(get_db)):
    success = crud.delete_pdf_file(db=db, user_email=user_email, docs_id=docs_id)
    if not success:
        raise HTTPException(status_code=404, detail="PDF file not found")
    return {"message": "PDF file deleted successfully"}

# -------------------
# 파이썬 서버 실행
# -------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True)