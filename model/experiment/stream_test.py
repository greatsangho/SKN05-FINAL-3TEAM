import os
from config.secret_keys import OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# define state
from typing_extensions import TypedDict
# define agent
from langchain_openai import ChatOpenAI
# define node
from langgraph.types import StreamWriter
# compile application
from langgraph.graph import StateGraph, START, END
# Fast API
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse






class State(TypedDict):
    question : str
    generation : str

llm = ChatOpenAI(
    model="gpt-4o-mini", 
    api_key=os.getenv("OPENAI_API_KEY")
)

async def generate(state : State, writer: StreamWriter):
    question = state["question"]

    chunks = []
    async for chunk in llm.astream(
        question
    ):
        writer(chunk)
        chunks.append(chunk.content)
    
    state["generation"] = "".join(chunks)

    return state






workflow = StateGraph(State)
workflow.add_node("generate", generate)
workflow.add_edge(START, "generate")
workflow.add_edge("generate", END)
app = workflow.compile()







server = FastAPI()

@server.get("/query")
async def query():
    async def answer_stream():
        try:
            async for chunk in app.astream(
                input={"question" : "안녕"}, stream_mode=["custom"]
            ):
                yield f"{chunk[1].content}"
        except Exception as e:
            yield f"Error message : {e}"
    
    return StreamingResponse(answer_stream(), media_type="text/event-stream")






if __name__ == "__main__":
    uvicorn.run("stream_test:server", host='localhost', reload=True)