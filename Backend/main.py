from fastapi import FastAPI, HTTPException, Request, Depends
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import uuid
import uvicorn
import requests

# Load environment variables
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# Add session middleware (required for OAuth)
app.add_middleware(SessionMiddleware, secret_key="your_consistent_secret_key")

# CORS configuration (adjust as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend domain in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 웹 상에서 구글 로그인 기능 --> 크롬 익스텐션에서 불필요하여 삭제(예정)
# Initialize OAuth client with required scopes
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/documents'
    },
    redirect_uri=REDIRECT_URI
)

# url/docs 로 기능 설명 페이지 안내
@app.get("/")
async def hello():
    return {"hello": "/docs for more info"}

# 구글 로그인 구현
@app.get("/auth/google")
async def login_with_google(request: Request):
    # Generate a unique state parameter using uuid
    state = str(uuid.uuid4())
    
    # Store the state in the session for validation during callback
    request.session['state'] = state
    
    # Redirect user to Google's OAuth2 authorization endpoint with the state parameter
    return await oauth.google.authorize_redirect(request, REDIRECT_URI, state=state)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    try:
        # Retrieve the stored state from the session
        stored_state = request.session.get('state')
        
        # Retrieve the returned state from Google's response
        returned_state = request.query_params.get('state')
        
        # Validate that the stored and returned states match
        if stored_state != returned_state:
            raise HTTPException(status_code=400, detail="State mismatch: Possible CSRF attack.")
        
        # Exchange authorization code for access token
        token = await oauth.google.authorize_access_token(request)
        
        # Retrieve user information from the token
        user_info = token.get('userinfo')
        
        return {"access_token": token, "user_info": user_info}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.post("/edit_doc")
async def edit_doc(file_id: str, content: str, token: str):
    """
    Edits a Google Doc by appending content to it.

    Args:
        file_id (str): The ID of the Google Doc.
        content (str): The content to append to the document.
        token (str): The OAuth access token.

    Returns:
        dict: The updated document details.
    """
    url = f"https://docs.googleapis.com/v1/documents/{file_id}:batchUpdate"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    body = {
        "requests": [
            {
                "insertText": {
                    "location": {
                        "index": 1  # Insert at the beginning of the document (index 1)
                    },
                    "text": content,
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())

# -------------------
# 데이터베이스 설정
# -------------------
# DATABASE_URL = "mysql+pymysql://<USER>:<PASSWORD>@<RDS_ENDPOINT>:3306/<DATABASE_NAME>"
DATABASE_URL = DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 질문/답변 모델 정의
class QuestionAnswer(Base):
    __tablename__ = "questions_answers"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)

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
# Pydantic 모델 정의
# -------------------
class QuestionCreate(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    id: int
    question: str
    answer: str | None

# -------------------
# RunPod 통신 함수
# -------------------
def send_to_runpod(question: str) -> str:
    url = "https://api.runpod.ai/v2/<POD_ID>/runsync"  # RunPod 엔드포인트 URL
    headers = {"Authorization": "Bearer <YOUR_API_KEY>"}
    body = {
        "input": {
            "api": {
                "method": "POST",
                "endpoint": "/generate",  # RunPod의 LLM 엔드포인트
            },
            "payload": {"question": question},
        }
    }
    response = requests.post(url, json=body, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json().get("output", {}).get("answer", "No answer received")

# -------------------
# API 엔드포인트 정의 (CRUD 포함)
# -------------------

# 질문 생성 및 RunPod 호출 엔드포인트 (CREATE)
@app.post("/questions", response_model=QuestionResponse)
async def create_question(question_data: QuestionCreate, db: Session = Depends(get_db)):
    # 질문 저장 (답변은 None 상태로 저장)
    question_entry = QuestionAnswer(question=question_data.question)
    db.add(question_entry)
    db.commit()
    db.refresh(question_entry)

    # RunPod에 질문 전송 및 답변 수신
    try:
        answer = send_to_runpod(question_data.question)
        question_entry.answer = answer  # 답변 업데이트
        db.commit()
        db.refresh(question_entry)
        return {"id": question_entry.id, "question": question_entry.question, "answer": question_entry.answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 모든 질문/답변 조회 (READ - 전체 조회)
@app.get("/questions", response_model=list[QuestionResponse])
async def get_all_questions(db: Session = Depends(get_db)):
    questions = db.query(QuestionAnswer).all()
    return [{"id": q.id, "question": q.question, "answer": q.answer} for q in questions]

# 특정 질문/답변 조회 (READ - 단일 조회)
@app.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(QuestionAnswer).filter(QuestionAnswer.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"id": question.id, "question": question.question, "answer": question.answer}

# 질문/답변 삭제 (DELETE)
@app.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(QuestionAnswer).filter(QuestionAnswer.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    db.commit()
    return {"message": f"Question with id {question_id} deleted"}

# 질문/답변 수정 (UPDATE)
@app.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, updated_data: QuestionCreate, db: Session = Depends(get_db)):
    question = db.query(QuestionAnswer).filter(QuestionAnswer.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # 질문 업데이트 및 RunPod 재호출
    try:
        question.question = updated_data.question
        answer = send_to_runpod(updated_data.question)  # 새로운 질문으로 RunPod 호출
        question.answer = answer
        db.commit()
        db.refresh(question)
        return {"id": question.id, "question": question.question, "answer": question.answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))