import os
from config.secret_keys import OPENAI_API_KEY, TAVILY_API_KEY, USER_AGENT, LANGSMITH_API_KEY, LANGSMITH_ENDPOINT, LANGSMITH_PROJECT, LANGSMITH_TRACING
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["USER_AGENT"] = USER_AGENT
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
from finpilot.experimental.paragraph import ParagraphProcess
from finpilot.experimental.utils import parse_pdf
from finpilot.experimental.vectorstore import create_empty_faiss, add_data_to_vectorstore
from langgraph.graph import StateGraph, START, END
from io import BytesIO
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from langsmith.utils import LangSmithMissingAPIKeyWarning
import warnings
warnings.filterwarnings("ignore", category=LangSmithMissingAPIKeyWarning)


###################### Define State ######################
class State(TypedDict):
    question : str
    generation : str
    documents : List[Document]
    messages : Annotated[List[BaseMessage], add_messages]
    source : List[str]



###################### Create Vector Store ######################
PDF_PATH = './data/pdf/도메인 특화 LLM Mistral 7B를 활용한 금융 업무분야 파인튜닝 및 활용 방법.pdf'
file_name = '도메인 특화 LLM Mistral 7B를 활용한 금융 업무분야 파인튜닝 및 활용 방법.pdf'
with open(PDF_PATH, 'rb') as file:
    document = parse_pdf(BytesIO(file.read()), file_name)
vector_store = create_empty_faiss()
vector_store = add_data_to_vectorstore(vector_store=vector_store, data=[document])



###################### Process Builder ######################
paragraph_process = ParagraphProcess(vector_store=vector_store)




###################### Build Application ######################
workflow = StateGraph(State)
# add node
workflow.add_node("retriever", paragraph_process.retrieve_node)
workflow.add_node("filter_documents", paragraph_process.filter_documents_node)
workflow.add_node("writer", paragraph_process.write_node)
workflow.add_node("improve_query", paragraph_process.improve_query_node)
workflow.add_node("web_search", paragraph_process.web_search_node)
# add edge
workflow.add_edge(START, "retriever")
workflow.add_edge("retriever", "filter_documents")
workflow.add_conditional_edges(
    "filter_documents",
    paragraph_process.decide_write_or_improve_query,
    {
        "writer" : "writer",
        "improve_query" : "improve_query"
    },
)
workflow.add_conditional_edges(
    "writer",
    paragraph_process.decide_to_regenerate_or_rewrite_query_or_end,
    {
        "not supported" : "writer",
        "useful" : END,
        "not useful" : "improve_query"
    }
)
workflow.add_edge("improve_query", "web_search")
workflow.add_edge("web_search", "retriever")
# compile
app = workflow.compile()



###################### Fast API Server ######################
server = FastAPI()
final_state = {}

# Stream Query
@server.get("/query")
async def stream_app():
    async def event_stream():
        global final_state
        try :
            async for stream_mode, chunk in app.astream(
                input={
                    "question" : "최근 LLM 동향에 대한 인사이트를 작성해줘", 
                    "documents" : []
                },
                stream_mode=[ "custom"]
            ):
                if isinstance(chunk, dict):
                    final_state = chunk
                else:
                    yield f"{chunk}"

        except Exception as e:
            raise HTTPException(500, f"Internel Server Error : \n{e}")
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# get source
@server.get("/get_source")
async def get_source():
    return JSONResponse(content={"source" : final_state["source"]})



if __name__ == "__main__":
    print("Start Server!")
    # app.get_graph().draw_mermaid_png(output_file_path="./charts/graph.png")
    uvicorn.run("stream_paragraph:server", host='localhost', reload=True)