from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
# from langgraph.checkpoint.memory import MemorySaver
from finpilot.memory import LimitedMemorySaver
from langgraph.graph import START, END, StateGraph
from langchain_community.vectorstores import FAISS

from finpilot.writer import WriterProcess
from finpilot.text_magician import TextMagicianProcess
from finpilot.web_visualizer import WebVisualizerProcess
from finpilot.inner_visualizer import InnerVisualizerProcess
from finpilot.draft import DraftProcess
from finpilot.router import route_question

def create_application(memory : LimitedMemorySaver, vector_store : FAISS, session_id : str):
    class State(TypedDict):
        """
        Represents the state of graph.

        Args:
            question : question that user ask
            generation : LLM generation
            documents : list of documents
        """
        chat_option : str
        question : str
        generation : str
        messages : Annotated[list, add_messages]
        documents : List[str]
        outlines : List[str]
        source : List[str]
    
    workflow = StateGraph(State)

    writer_process = WriterProcess(vector_store=vector_store)
    text_magician_process = TextMagicianProcess()
    web_visualizer_process = WebVisualizerProcess(session_id=session_id)
    inner_visualizer_process = InnerVisualizerProcess(session_id=session_id)
    draft_process = DraftProcess(session_id=session_id)

    ################## Add Nodes ##################

    ## writer
    workflow.add_node("retriever", writer_process.retrieve_node)
    workflow.add_node("filter_documents", writer_process.filter_documents_node)
    workflow.add_node("writer", writer_process.write_node)
    workflow.add_node("improve_query", writer_process.improve_query_node)
    workflow.add_node("web_search", writer_process.web_search_node)

    ## text_magician
    workflow.add_node("text_magician", text_magician_process.text_magician_node)

    ## web_visualizer
    workflow.add_node("web_visualizer", web_visualizer_process.web_visualizer_node)
    workflow.add_node("tool", web_visualizer_process.tool_node)

    ## inner_visualizer
    workflow.add_node("inner_visualizer", inner_visualizer_process.inner_visualizer_node)

    ## draft
    workflow.add_node("make_outline_node", draft_process.make_outline_node)
    workflow.add_node("write_draft_paragraph_node", draft_process.write_draft_paragraph_node)
    

    ################## add edges ##################
    ## Route Question
    workflow.add_conditional_edges(
        START,
        route_question,
        {
            "writer" : "retriever",
            "text_magician" : "text_magician",
            "web_visualizer" : "web_visualizer",
            "inner_visualizer" : "inner_visualizer",
            "draft" : "make_outline_node"
        }
    )

    # writer process
    workflow.add_edge("retriever", "filter_documents")
    workflow.add_conditional_edges(
        "filter_documents",
        writer_process.decide_write_or_improve_query,
        {
            "writer" : "writer",
            "improve_query" : "improve_query"
        },
    )
    workflow.add_conditional_edges(
        "writer",
        writer_process.decide_to_regenerate_or_rewrite_query_or_end,
        {
            "not supported" : "writer",
            "useful" : END,
            "not useful" : "improve_query"
        }
    )
    workflow.add_edge("improve_query", "web_search")
    workflow.add_edge("web_search", "retriever")

    # text_magician process
    workflow.add_edge("text_magician", END)


    # web_visualizer process
    workflow.add_conditional_edges(
        "web_visualizer",
        web_visualizer_process.should_continue,
        {
            "continue" : "tool",
            "end" : END
        }
    )
    workflow.add_edge("tool", "web_visualizer")


    # inner_visualizer process
    workflow.add_edge("inner_visualizer", END)


    # draft process
    workflow.add_edge("make_outline_node", "write_draft_paragraph_node")
    workflow.add_conditional_edges(
        "write_draft_paragraph_node",
        draft_process.should_continue,
        {
            "end" : END,
            "continue" : "write_draft_paragraph_node"
        }
    )



    ################## Compile Workflow ##################
    app = workflow.compile(checkpointer=memory)
    
    return app