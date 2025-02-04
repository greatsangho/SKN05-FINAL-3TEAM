################################## Import Modules ##################################
# Base Modules
import os
from pathlib import Path
# FinPilot Modules
from finpilot.request_model import QueryRequestModel, DeleteFileRequestModel
from finpilot.vectorstore import add_data_to_vectorstore_and_update_redis, delete_data_from_vectorstore_and_update_redis
from finpilot.session import get_session_app, get_session_vectorstore
from finpilot.utils import parse_pdf, delete_files_in_dir, encode_img_base64
# Server Modules
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.responses import JSONResponse
import uvicorn
from redis import Redis
# Ignore Warnings
import warnings
from langsmith.utils import LangSmithMissingAPIKeyWarning
warnings.filterwarnings("ignore", category=LangSmithMissingAPIKeyWarning)





################################## Environment Variable Setting ##################################
from config.secret_keys import OPENAI_API_KEY, TAVILY_API_KEY, USER_AGENT, DART_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["USER_AGENT"] = USER_AGENT
os.environ["DART_API_KEY"] = DART_API_KEY




################################## Create Redis Client ##################################
redis = Redis(host="localhost", port=6379, decode_responses=False)





################################## Initialize Fast API server ##################################
app = FastAPI()





################################## Invoke Answer (Non Image) ##################################
@app.post("/query")
async def query(
    request : QueryRequestModel
):
    # Get Session ID
    session_id = request.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required!")
    # Get question
    question = request.question
    if not question:
        raise HTTPException(status_code=400, detail="Question is required!")
    # Get Chat option
    chat_option = request.chat_option
    if not chat_option:
        raise HTTPException(status_code=400, detail="Chat Option is required!")
    
    # Create/Load the LangGraph Application according to Session ID
    pilot = get_session_app(
        redis_client=redis,
        session_id=session_id
    )
    
    # Set Data Path for Get CSV Data
    data_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    
    if not "데이터 시각화" in chat_option:
        # invoke answer
        print("[Server Log] INVOKING PILOT ANSWER (NON-IMAGE)")
        answer = pilot.invoke(question, session_id, chat_option)
        print("[Server Log] PILOT ANSWER INVOKED")

        # delete LangGraph Application
        del pilot

        if len(os.listdir(data_path)) > 0:
            delete_files_in_dir(data_path)

        # return answer
        return {"session_id" : session_id, "answer" : answer["generation"], "source" : answer["source"]}
    else:
        # Set Folder Path for Image saving
        chart_path = f"./charts/{session_id}/"
        if not os.path.exists(chart_path):
            os.makedirs(chart_path)

        # invoke answer
        print("[Server Log] INVOKING PILOT ANSWER (NON-IMAGE)")
        while len(os.listdir(chart_path)) == 0:
            answer = pilot.invoke(question, session_id, chat_option)
        print("[Server Log] PILOT ANSWER INVOKED")

        # delete LangGraph Application
        del pilot

        # Get PNG File list
        png_files = [f for f in os.listdir(chart_path) if f.endswith(".png")]
        if not png_files:
            raise HTTPException(status_code=404, detail="No PNG files found in the folder")

        # Encode Image to Base64 type
        images = encode_img_base64(chart_path, png_files)

        if chat_option == "데이터 시각화 (Upload)":
            # Delete Remaining CSV Files
            if len(os.listdir(data_path)) > 0:
                delete_files_in_dir(data_path)

        
        return JSONResponse(content={"images": images, "source" : answer["source"]})



################################## Upload File (PDF) ##################################
@app.post("/pdfs/upload")
async def upload_pdf(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    # Check File Type is PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Not a PDF file!")
    
    # Parsing PDF File And Transform as Document object
    documents = []
    document = parse_pdf(file)
    documents.append(document)

    # Get VectorStore accoring to Session ID
    vectorstore = get_session_vectorstore(
        redis_client=redis,
        session_id=session_id
    )

    # Add data to Session VectorStore & Update Redis Server Data
    add_data_to_vectorstore_and_update_redis(
        redis_client=redis,
        session_id=session_id,
        vector_store=vectorstore,
        data=documents
    )

    del vectorstore

    # Return Status (Task Complete)
    return {"status" : "success"}





################################## Upload File (CSV) ##################################
@app.post("/csvs/upload")
async def upload_csv(
    session_id : str = Form(...),
    file : UploadFile = File(...)
):
    # Set Path to save CSV File
    upload_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    # Delete Any Remaing CSV Files
    if len(os.listdir(upload_path)) > 0:
        delete_files_in_dir(upload_path)

    # Set File Path
    upload_file_path = upload_path / file.filename

    # Save File to Local dir
    try :
        with open(upload_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error ocurred : {e}")
    
    # Return Status (Task Complete)
    return {"status" : "success"}





################################## Delete File (PDF) ##################################
@app.post("/pdfs/delete")
async def delete_pdf(
    request : DeleteFileRequestModel
):
    # Get file name
    file_name = request.file_name
    # Get Session ID
    session_id = request.session_id

    # Get VectorStore accoring to Session ID
    vectorstore = get_session_vectorstore(
        redis_client=redis,
        session_id=session_id
    )
    
    # delete data from Session VectorStore & Update Redis Server Data
    delete_data_from_vectorstore_and_update_redis(
        redis_client=redis,
        session_id=session_id,
        vector_store=vectorstore,
        file_name=file_name
    )

    del vectorstore

    # Return Status (Task Complete)
    return {"status" : "success"}





################################## Delete File (CSV) ##################################
@app.post("/csvs/delete")
async def delete_csv(
    request : DeleteFileRequestModel
):
    # Get Session ID
    session_id = request.session_id
    
    # Set Path to delete CSV File
    delete_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(delete_path):
        os.makedirs(delete_path)
    
    # Delete Any Remaing CSV Files
    if len(os.listdir(delete_path)) > 0:
        delete_files_in_dir(delete_path)
    
    # Return Status (Task Complete)
    return {"status" : "success"}





################################## 활성화 세션 정보 확인 ##################################
@app.get("/sessions")
async def list_sessions():
    # Redis에서 활성 세션 리스트 반환
    keys = redis.keys("*")
    return {"active_sessions" : [key for key in keys]}




################################## Fast API Server 실행 ##################################
if __name__ == "__main__" :
    # uvicorn.run("main:app", host="0.0.0.0", port=8000) # 배포
    uvicorn.run("app:app", host='localhost', reload=True) # 로컬 테스트