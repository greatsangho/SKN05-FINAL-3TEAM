import dill
import base64

# FinPilot Application
from finpilot.core import FinPilot
from finpilot.memory import LimitedMemorySaver
from finpilot.request_model import QueryRequestModel, UploadPDFRequestModel, DeletePDFRequestModel
from finpilot.vectorstore import load_faiss_from_redis, create_empty_faiss, save_faiss_to_redis, add_data_to_vectorstore_and_update_redis, delete_data_from_vectorstore_and_update_redis

from langchain_core.documents import Document
import pymupdf4llm
import fitz

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
from redis import Redis

import warnings
from langsmith.utils import LangSmithMissingAPIKeyWarning

# 특정 경고 무시
warnings.filterwarnings("ignore", category=LangSmithMissingAPIKeyWarning)


import os
from pathlib import Path

# Environment Variable Setting
from config.secret_keys import OPENAI_API_KEY, TAVILY_API_KEY, USER_AGENT, POLYGON_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["USER_AGENT"] = USER_AGENT
os.environ["POLYGON_API_KEY"] = POLYGON_API_KEY



# Redis 연결
redis = Redis(host="localhost", port=6379, decode_responses=False)


def get_session_app(session_id):
    # Redis 에서 session data 로드
    if redis.exists(f"{session_id}_memory_saver"):
        memory = dill.loads(redis.get(f"{session_id}_memory_saver"))
        vectorstore = load_faiss_from_redis(redis_client=redis, session_id=session_id)
        pilot = FinPilot(memory=memory, vector_store=vectorstore, session_id=session_id)
        print(f"[Server Log] Application Loaded for session id : {session_id}")
    else:
        # 새로운 세션 생성 및 Redis에 저장
        memory = LimitedMemorySaver(capacity=10)
        vectorstore = create_empty_faiss()
        pilot = FinPilot(memory=memory, vector_store=vectorstore, session_id=session_id)
        
        redis.set(f"{session_id}_memory_saver", dill.dumps(memory))
        redis.expire(f"{session_id}_memory_saver", 3600)
        save_faiss_to_redis(
            redis_client=redis,
            session_id=session_id,
            vector_store=vectorstore
        )
        
    return pilot


def get_session_vectorstore(session_id):
    # Redis 에서 session data 로드
    if redis.exists(f"{session_id}_faiss_index"):
        vectorstore = load_faiss_from_redis(redis_client=redis, session_id=session_id)
        print(f"[Server Log] VectorStore Loaded for session id : {session_id}")
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

@app.post("/upload-csv")
async def upload_csv(
    session_id : str = Form(...),
    csv_file : UploadFile = File(...)
):
    upload_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    if len(os.listdir(upload_path)) > 0:
        try:
            for filename in os.listdir(upload_path):
                file_path = os.path.join(upload_path, filename)
                
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"[Server Log] FILE REMOVED: {file_path}")
                elif os.path.isdir(file_path):
                    print(f"[Server Log] REMOVE FAILED (DIR) : {file_path}")
            
            print(f"[Server Log] REMOVED ALL FILES IN PATH : '{upload_path}'")
        except Exception as e:
            print(f"[Server Log] ERROR : {e}")
    
    upload_file_path = upload_path / csv_file.filename

    try :
        with open(upload_file_path, "wb") as f:
            content = await csv_file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error ocurred : {e}")



@app.post("/delete-pdf")
async def delete_pdf(json : DeletePDFRequestModel):
    file_name = json.file_name
    session_id = json.session_id

    vectorstore = get_session_vectorstore(session_id)

    delete_data_from_vectorstore_and_update_redis(
        redis_client=redis,
        session_id=session_id,
        vector_store=vectorstore,
        file_name=file_name
    )

@app.post("/get-graph-image")
async def get_graph_image(json : QueryRequestModel):
    json_input = json.input
    session_id = json_input.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required!")
    
    pilot = get_session_app(session_id)

    question = json_input.question
    if not question:
        raise HTTPException(status_code=400, detail="Question is required!")


    folder_path = f"./charts/{session_id}/"
    data_path = Path(os.getcwd()) / "data" / f"{session_id}"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


    _ = pilot.invoke(question, session_id)


    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # PNG 파일 목록 가져오기
    png_files = [f for f in os.listdir(folder_path) if f.endswith(".png")]
    
    if not png_files:
        raise HTTPException(status_code=404, detail="No PNG files found in the folder")

    # 이미지 데이터를 Base64로 인코딩
    images = []
    for file_name in png_files:
        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
                images.append({"file_name": file_name, "image_data": img_base64})
            
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file {file_name}: {str(e)}")
    
    if len(os.listdir(data_path)) > 0:
        try:
            for filename in os.listdir(data_path):
                file_path = os.path.join(data_path, filename)
                
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"[Server Log] FILE REMOVED: {file_path}")
                elif os.path.isdir(file_path):
                    print(f"[Server Log] REMOVE FAILED (DIR) : {file_path}")
            
            print(f"[Server Log] REMOVED ALL FILES IN PATH : '{data_path}'")
        except Exception as e:
            print(f"[Server Log] ERROR : {e}")
    
    # JSON 형태로 반환
    return JSONResponse(content={"images": images})

@app.get("/sessions")
async def list_sessions():
    # Redis에서 활성 세션 리스트 반환
    keys = redis.keys("*")
    return {"active_sessions" : [key for key in keys]}


if __name__ == "__main__" :
    uvicorn.run("main:app", host="127.0.0.1", reload=True)