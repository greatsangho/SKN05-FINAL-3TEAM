from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph

from finpilot.writer import WriterProcess
from finpilot.text_magician import TextMagicianProcess
from finpilot.web_visualizer import WebVisualizerProcess
from finpilot.inner_visualizer import InnerVisualizerProcess
from finpilot.router import route_question

def get_application():
    class State(TypedDict):
        """
        Represents the state of graph.

        Args:
            question : question that user ask
            generation : LLM generation
            documents : list of documents
        """
        question : str
        generation : str
        messages : Annotated[list, add_messages]
        documents : List[str]
        
    memory = MemorySaver()
    
    workflow = StateGraph(State)

    writer_process = WriterProcess()
    text_magician_process = TextMagicianProcess()
    web_visualizer_process = WebVisualizerProcess()
    inner_visualizer_process = InnerVisualizerProcess()

    ################## Add Nodes ##################

    ## writer
    workflow.add_node("retriever", writer_process.retrieve_node)
    workflow.add_node("filter_documents", writer_process.filter_documents_node)
    workflow.add_node("writer", writer_process.write_node)
    workflow.add_node("transform_query", writer_process.transform_query_node)
    workflow.add_node("web_search", writer_process.web_search_node)

    ## text_magician
    workflow.add_node("text_magician", text_magician_process.text_magician_node)

    ## web_visualizer
    workflow.add_node("web_visualizer", web_visualizer_process.web_visualizer_node)
    workflow.add_node("tool", web_visualizer_process.tool_node)

    ## inner_visualizer
    workflow.add_node("inner_visualizer", inner_visualizer_process.inner_visualizer_node)


    ################## add edges ##################
    ## Route Question
    workflow.add_conditional_edges(
        START,
        route_question,
        {
            "writer" : "retriever",
            "text_magician" : "text_magician",
            "web_visualizer" : "web_visualizer",
            "inner_visualizer" : "inner_visualizer"
        }
    )

    # writer process
    workflow.add_edge("retriever", "filter_documents")
    workflow.add_conditional_edges(
        "filter_documents",
        writer_process.decide_write_or_rewrite_query,
        {
            "writer" : "writer",
            "transform_query" : "transform_query"
        },
    )
    workflow.add_conditional_edges(
        "transform_query",
        writer_process.decide_to_retrieve_or_web_search,
        {
            "retriever" : "retriever",
            "web_search" : "web_search"
        }
    )
    workflow.add_edge("web_search", "writer")
    workflow.add_conditional_edges(
        "writer",
        writer_process.decide_to_regenerate_or_rewrite_query_or_end,
        {
            "not supported" : "writer",
            "useful" : END,
            "not useful" : "transform_query"
        }
    )

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



    ################## Compile Workflow ##################
    app = workflow.compile(checkpointer=memory)
    
    return app