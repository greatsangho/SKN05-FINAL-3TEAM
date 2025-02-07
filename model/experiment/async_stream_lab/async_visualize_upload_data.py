import os
from config.secret_keys import OPENAI_API_KEY, LANGSMITH_API_KEY, LANGSMITH_ENDPOINT, LANGSMITH_PROJECT, LANGSMITH_TRACING
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
os.environ["LANGSMITH_TRACING"] = LANGSMITH_TRACING

from typing_extensions import TypedDict
from typing import Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

from langgraph.graph import StateGraph, START, END
from finpilot.experimental.visualize_upload_data import VisualizeUploadDataProcess

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pathlib import Path
from finpilot.experimental.utils import encode_img_base64



class State(TypedDict):
    question : str
    generation : str
    messages : Annotated[List[BaseMessage], add_messages]
    documents : List[Document]
    source : List[str]


visualize_upload_data_process = VisualizeUploadDataProcess(session_id="session_tmp")

workflow = StateGraph(State)

workflow.add_node("visualize_node", visualize_upload_data_process.visualize_node)

workflow.add_edge(START, "visualize_node")
workflow.add_conditional_edges(
    "visualize_node",
    visualize_upload_data_process.should_continue,
    {
        "continue" : "visualize_node",
        "end" : END
    }
)

app = workflow.compile()




server = FastAPI()

@server.get("/query")
async def query():
    # Set Folder Path for Image saving
    folder_path = f"./charts/session_tmp/"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Set Data Path for Get CSV Data
    data_path = Path(os.getcwd()) / "data" / f"session_tmp"
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    
    print("[Server Log] INVOKING PILOT ANSWER (IMAGE)")
    answer = await app.ainvoke(
        {"question" : "주어진 데이터를 다양한 시각에서 분석하여 시각화해줘줘"}
    )
    print("[Server Log] PILOT ANSWER INVOKED")

    png_files = [f for f in os.listdir(folder_path) if f.endswith(".png")]
    if not png_files:
        raise HTTPException(status_code=404, detail="No PNG files found in the folder")

    # Encode Image to Base64 type
    images = encode_img_base64(folder_path, png_files)
    

    # Return Image data as JSON Form
    return JSONResponse(content={"images": images, "source" : answer["source"]})



if __name__ == "__main__":
    uvicorn.run("async_visualize_upload_data:server", host="localhost", reload=True)