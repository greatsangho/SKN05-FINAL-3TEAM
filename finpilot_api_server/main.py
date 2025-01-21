import os
from pathlib import Path

# FinPilot Application
from finpilot.request_model import QueryRequestModel, UploadPDFRequestModel, DeletePDFRequestModel, UploadCSVRequestModel
from finpilot.vectorstore import add_data_to_vectorstore_and_update_redis, delete_data_from_vectorstore_and_update_redis
from finpilot.session import get_session_app, get_session_vectorstore
from finpilot.utils import parse_pdf, delete_files_in_dir, encode_img_base64

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
from redis import Redis

# 특정 경고 무시
import warnings
from langsmith.utils import LangSmithMissingAPIKeyWarning
warnings.filterwarnings("ignore", category=LangSmithMissingAPIKeyWarning)




# Environment Variable Setting
# from config.secret_keys import OPENAI_API_KEY, TAVILY_API_KEY, USER_AGENT, POLYGON_API_KEY
# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
# os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
# os.environ["USER_AGENT"] = USER_AGENT
# os.environ["POLYGON_API_KEY"] = POLYGON_API_KEY



# Redis 연결
redis = Redis(host="localhost", port=6379, decode_responses=False)




app = FastAPI()

@app.post("/query")
async def finpilot_endpoint(request : QueryRequestModel):
    # Session ID 가져오기
    session_id = request.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required!")
    
    question = request.question
    if not question:
        raise HTTPException(status_code=400, detail="Question is required!")
    
    chat_option = request.chat_option
    if not chat_option:
        raise HTTPException(status_code=400, detail="Chat Option is required!")
    

    pilot = get_session_app(
        redis_client=redis,
        session_id=session_id
    )
    
    answer = pilot.invoke(question, session_id, chat_option)

    return {"session_id" : session_id, "answer" : answer}


@app.post("/get-graph-image")
async def get_graph_image(request : QueryRequestModel):

    session_id = request.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required!")
    
    question = request.question
    if not question:
        raise HTTPException(status_code=400, detail="Question is required!")
    
    chat_option = request.chat_option
    if not chat_option:
        raise HTTPException(status_code=400, detail="Chat Option is required!")
    

    folder_path = f"./charts/{session_id}/"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    data_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(data_path):
        os.makedirs(data_path)


    pilot = get_session_app(
        redis_client=redis,
        session_id=session_id
    )

    while len(os.listdir(folder_path)) == 0:
        _ = pilot.invoke(question, session_id, chat_option)

    
    # PNG 파일 목록 가져오기
    png_files = [f for f in os.listdir(folder_path) if f.endswith(".png")]
    if not png_files:
        raise HTTPException(status_code=404, detail="No PNG files found in the folder")


    # 이미지 데이터를 Base64로 인코딩
    images = encode_img_base64(folder_path, png_files)
    

    if len(os.listdir(data_path)) > 0:
        delete_files_in_dir(data_path)
    

    # JSON 형태로 반환
    return JSONResponse(content={"images": images})


@app.post("/upload-pdf")
async def upload_pdf(
    # request : UploadPDFRequestModel
    session_id: str = Form(...),  # 문자열은 Form 필드로 처리
    file: UploadFile = File(...)  # 파일 업로드는 File로 처리
):
    # file = request.file
    # session_id = request.session_id

    documents = []

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Not a PDF file!")
    
    document = parse_pdf(file)
    documents.append(document)

    vectorstore = get_session_vectorstore(
        redis_client=redis,
        session_id=session_id
    )

    add_data_to_vectorstore_and_update_redis(
        redis_client=redis,
        session_id=session_id,
        vector_store=vectorstore,
        data=documents
    )

    return {"status" : "success"}



@app.post("/upload-csv")
async def upload_csv(
    # request : UploadCSVRequestModel
    session_id : str = Form(...),
    file : UploadFile = File(...)
):
    # session_id = request.session_id
    # file = request.file

    upload_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    if len(os.listdir(upload_path)) > 0:
        delete_files_in_dir(upload_path)

    
    upload_file_path = upload_path / file.filename

    try :
        with open(upload_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error ocurred : {e}")
    
    return {"status" : "success"}


@app.post("/delete-pdf")
async def delete_pdf(json : DeletePDFRequestModel):
    file_name = json.file_name
    session_id = json.session_id

    vectorstore = get_session_vectorstore(
        redis_client=redis,
        session_id=session_id
    )

    delete_data_from_vectorstore_and_update_redis(
        redis_client=redis,
        session_id=session_id,
        vector_store=vectorstore,
        file_name=file_name
    )

    return {"status" : "success"}


@app.get("/sessions")
async def list_sessions():
    # Redis에서 활성 세션 리스트 반환
    keys = redis.keys("*")
    return {"active_sessions" : [key for key in keys]}




if __name__ == "__main__" :
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # uvicorn.run("main:app", host='localhost', reload=True)