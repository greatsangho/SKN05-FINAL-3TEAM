import os
from config.secret_keys import OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from typing_extensions import TypedDict
from typing import Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

from finpilot.experimental.writer import WriterProcess



class State(TypedDict):
    question : str
    generation : str
    document : List[Document]
    messages : Annotated[List[BaseMessage], add_messages]
    source : List[str]

