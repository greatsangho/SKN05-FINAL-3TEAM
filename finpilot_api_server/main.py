# Session Cache
from functools import lru_cache
import dill

# FinPilot Application
from finpilot.core import FinPilot
from finpilot.memory import LimitedMemorySaver
from finpilot.request_model import QueryRequestModel, UploadPDFRequestModel
from finpilot.vectorstore import load_faiss_from_redis, create_empty_faiss, save_faiss_to_redis, add_data_to_vectorstore_and_update_redis

from langchain_core.documents import Document
import pymupdf4llm
import fitz

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
import uvicorn
from redis import Redis

# Environment Variable Setting
import os
from config.secret_keys import OPENAI_API_KEY, TAVILY_API_KEY, USER_AGENT, POLYGON_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["USER_AGENT"] = USER_AGENT
os.environ["POLYGON_API_KEY"] = POLYGON_API_KEY



# Redis 연결
redis = Redis(host="localhost", port=6379, decode_responses=False)

@lru_cache(maxsize=100)
def get_session_app(session_id):
    # Redis 에서 session data 로드
    if redis.exists(f"{session_id}_memory_saver"):
        memory = dill.loads(redis.get(f"{session_id}_memory_saver"))
        vectorstore = load_faiss_from_redis(redis_client=redis, session_id=session_id)
        pilot = FinPilot(memory=memory, vector_store=vectorstore)
    else:
        # 새로운 세션 생성 및 Redis에 저장
        memory = LimitedMemorySaver(capacity=10)
        vectorstore = create_empty_faiss()
        pilot = FinPilot(memory=memory, vector_store=vectorstore)
        
        redis.set(f"{session_id}_memory_saver", dill.dumps(memory))
        redis.expire(f"{session_id}_memory_saver", 3600)
        save_faiss_to_redis(
            redis_client=redis,
            session_id=session_id,
            vector_store=vectorstore
        )
        
    return pilot


@lru_cache(maxsize=100)
def get_session_vectorstore(session_id):
    # Redis 에서 session data 로드
    if redis.exists(f"{session_id}_faiss_index"):
        vectorstore = load_faiss_from_redis(redis_client=redis, session_id=session_id)
    else:
        # 새로운 세션 생성 및 Redis에 저장
        memory = LimitedMemorySaver(capacity=10)
        vectorstore = create_empty_faiss()
        
        redis.set(f"{session_id}_memory_saver", dill.dumps(memory))
        redis.expire(f"{session_id}_memory_saver", 3600)
        save_faiss_to_redis(
            redis_client=redis,
            session_id=session_id,
            vector_store=vectorstore
        )


    return vectorstore

def parse_pdf(file : UploadFile) -> Document:
    # Pdf Parsing
    page_content = pymupdf4llm.to_markdown(fitz.open(stream=file.file.read(), filetype="pdf"), show_progress=True)

    return Document(
        page_content=page_content,
        metadata={
            "filename" : file.filename
        }
    )







app = FastAPI()

@app.post("/query")
async def finpilot_endpoint(json : QueryRequestModel):
    json_input = json.input
    # Session ID 가져오기
    session_id = json_input.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required!")
    
    pilot = get_session_app(session_id)

    question = json_input.question
    if not question:
        raise HTTPException(status_code=400, detail="Question is required!")
    
    answer = pilot.invoke(question, session_id)

    return {"session_id" : session_id, "answer" : answer}



@app.post("/upload-pdf")
async def upload_pdf(
    session_id: str = Form(...),  # 문자열은 Form 필드로 처리
    pdf_files: list[UploadFile] = File(...)  # 파일 업로드는 File로 처리
):
    # files = json['pdf_files']
    # session_id = json['session_id']

    documents = []

    for file in pdf_files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Not a PDF file!")
        
        document = parse_pdf(file)
        documents.append(document)

    vectorstore = get_session_vectorstore(session_id)

    add_data_to_vectorstore_and_update_redis(
        redis_client=redis,
        session_id=session_id,
        vector_store=vectorstore,
        data=documents
    )
        

@app.get("/sessions")
async def list_sessions():
    # Redis에서 활성 세션 리스트 반환
    keys = redis.keys("*")
    return {"active_sessions" : [key for key in keys]}


if __name__ == "__main__" :
    uvicorn.run("main:app", host="127.0.0.1", reload=True)