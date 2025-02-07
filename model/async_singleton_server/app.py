################################## Import Modules ##################################
# Base Modules
import os
from pathlib import Path
import asyncio
# FinPilot Modules
from finpilot.request_model import QueryRequestModel, DeleteFileRequestModel
from finpilot.vectorstore import add_data_to_vectorstore
from finpilot.vectorstore import delete_data_from_vectorstore
from finpilot.core import get_finpilot
from finpilot.utils import parse_pdf, delete_files_in_dir, encode_img_base64
# Server Modules
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.responses import JSONResponse
import uvicorn
# Ignore Warnings
# import warnings
# from langsmith.utils import LangSmithMissingAPIKeyWarning
# warnings.filterwarnings("ignore", category=LangSmithMissingAPIKeyWarning)

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings





################################## Environment Variable Setting ##################################
from config.secret_keys import OPENAI_API_KEY, TAVILY_API_KEY, USER_AGENT, DART_API_KEY
from config.secret_keys import LANGSMITH_API_KEY, LANGSMITH_ENDPOINT, LANGSMITH_PROJECT, LANGSMITH_TRACING
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["USER_AGENT"] = USER_AGENT
os.environ["DART_API_KEY"] = DART_API_KEY
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
os.environ["LANGSMITH_TRACING"] = LANGSMITH_TRACING



################################## Initialize Fast API server ##################################
app = FastAPI()




################################## Initialize Chroma Vector DB ##################################
vector_store = Chroma(
    embedding_function=OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY")
    ),
    persist_directory="ChromaDB",
)



################################## Initialize FinPilot Application ##################################
pilot = get_finpilot(
    vector_store=vector_store
)


################################## Invoke Answer ##################################
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

    input = {
        "question" : question,
        "chat_option" : chat_option,
        "session_id" : session_id,
        "documents" : [],
        "generation" : "",
        "source" : []
    }

    config = {
        "configurable" : {"thread_id" : session_id},
        "recursion_limit" : 40
    }

    # Set Data Path for Get CSV Data
    data_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    
    if not "데이터 시각화" in chat_option:
        # invoke answer
        print("[Server Log] INVOKING PILOT ANSWER (NON-IMAGE)")
        answer = await pilot.ainvoke(input=input, config=config)
        print("[Server Log] PILOT ANSWER INVOKED")

        if len(os.listdir(data_path)) > 0:
            await delete_files_in_dir(data_path)

        # return answer
        return JSONResponse(content={
            "answer" : answer["generation"],
            "source" : answer.get("source", [])
        })
        
    else:
        # Set Folder Path for Image saving
        chart_path = f"./charts/{session_id}/"
        if not os.path.exists(chart_path):
            os.makedirs(chart_path)

        # invoke answer
        print("[Server Log] INVOKING PILOT ANSWER (IMAGE)")
        answer = await pilot.ainvoke(input=input, config=config)
        print("[Server Log] PILOT ANSWER INVOKED")

        # Get PNG File list
        png_files = [f for f in os.listdir(chart_path) if f.endswith(".png")]
        if not png_files:
            raise HTTPException(status_code=404, detail="No PNG files found in the folder")

        # Encode Image to Base64 type
        images = await encode_img_base64(chart_path, png_files, source=answer["source"])

        if chat_option == "데이터 시각화 (Upload)":
            # Delete Remaining CSV Files
            if len(os.listdir(data_path)) > 0:
                await delete_files_in_dir(data_path)
        
        return JSONResponse(content={
            "images": images
        })



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
    document = await parse_pdf(
        file=file, 
        session_id=session_id
    )
    documents.append(document)

    global vector_store
    vector_store = await add_data_to_vectorstore(
        vector_store=vector_store,
        data=documents
    )

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
        await delete_files_in_dir(upload_path)

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
    
    # delete data from Session VectorStore & Update Redis Server Data
    global vector_store
    vector_store = await delete_data_from_vectorstore(
        vector_store=vector_store,
        file_name=file_name,
        session_id=session_id
    )

    # del vectorstore

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
        await delete_files_in_dir(delete_path)
    
    # Return Status (Task Complete)
    return {"status" : "success"}




################################## Fast API Server 실행 ##################################
if __name__ == "__main__" :
    uvicorn.run("app:app", host='localhost', reload=True)