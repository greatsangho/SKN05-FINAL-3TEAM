import os
from config.secret_keys import OPENAI_API_KEY, LANGSMITH_API_KEY, LANGSMITH_ENDPOINT, LANGSMITH_PROJECT, LANGSMITH_TRACING
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
os.environ["LANGSMITH_TRACING"] = LANGSMITH_TRACING

###################### Import Modules ######################
from typing_extensions import TypedDict
from typing import Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

from finpilot.experimental.length_control import LengthControlProcess

from langgraph.graph import StateGraph, START, END

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse



###################### Define State ######################
class State(TypedDict):
    question : str
    generation : str
    documents : List[Document]
    messages : Annotated[List[BaseMessage], add_messages]
    source : List[str]



length_control_process = LengthControlProcess()

workflow = StateGraph(State)

workflow.add_node("length_control", length_control_process.length_control_node)

workflow.add_edge(START, "length_control")
workflow.add_edge("length_control", END)

app = workflow.compile()




server = FastAPI()

@server.get("/query")
async def query():
    async def event_stream():
        try:
            async for stream_mode, chunk in app.astream(
                input={
                    "question" : "동해물과 백두산이 마르고 닳도록. 이 문장의 분량을 늘려줘",
                },
                stream_mode=["custom"]
            ):
                yield f"{chunk}"
        except Exception as e:
            raise HTTPException(500, f"Internel Server Error : \n{e}")

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run("stream_length_control:server", host='localhost', reload=True)
        