############################### Import Modules ###############################
from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from finpilot.memory import LimitedMemorySaver
from langgraph.graph import START, END, StateGraph
from langchain_community.vectorstores import FAISS

from finpilot.paragraph import ParagraphProcess
from finpilot.length_control import LengthControlProcess
from finpilot.visualize_web_data import VisualizeWebDataProcess
from finpilot.visualize_upload_data import VisualizeUploadDataProcess
from finpilot.draft import DraftProcess
from finpilot.router import route_question

def get_finpilot( 
        vector_store : FAISS, 
    ):
    class State(TypedDict):
        """
        Represents the state of graph.

        Args:
            question : question that user ask
            generation : LLM generation
            documents : list of documents
        """
        chat_option : str
        session_id : str
        question : str
        generation : str
        messages : Annotated[list, add_messages]
        documents : List[str]
        outlines : List[str]
        source : List[str]

    limited_memory = LimitedMemorySaver(capacity=10)
    workflow = StateGraph(State)

    paragraph_process = ParagraphProcess(vector_store=vector_store)
    length_control_process = LengthControlProcess()
    visualize_web_data_process = VisualizeWebDataProcess()
    visualize_upload_data_process = VisualizeUploadDataProcess()
    draft_process = DraftProcess()

    ################## Add Nodes ##################

    # paragraph
    workflow.add_node("retriever", paragraph_process.retrieve_node)
    workflow.add_node("filter_documents", paragraph_process.filter_documents_node)
    workflow.add_node("writer", paragraph_process.write_node)
    workflow.add_node("improve_query", paragraph_process.improve_query_node)
    workflow.add_node("web_search", paragraph_process.web_search_node)

    # length control
    workflow.add_node("length_control", length_control_process.length_control_node)

    # visualize web data
    workflow.add_node("visualize_web_node", visualize_web_data_process.visualize_node)
    workflow.add_node("tool_node", visualize_web_data_process.tool_node)

    # visualize upload data
    workflow.add_node("visualize_upload_node", visualize_upload_data_process.visualize_node)

    # draft
    workflow.add_node("make_outline_node", draft_process.make_outline_node)
    workflow.add_node("write_draft_paragraph_node", draft_process.write_draft_paragraph_node)
    

    ################## add edges ##################
    ## Route Question
    workflow.add_conditional_edges(
        START,
        route_question,
        {
            "paragraph" : "retriever",
            "length_control" : "length_control",
            "visualize_web_data" : "visualize_web_node",
            "visualize_upload_data" : "visualize_upload_node",
            "draft" : "make_outline_node"
        }
    )

    # writer process
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

    # text_magician process
    workflow.add_edge("length_control", END)


    # visualize_web_data process
    workflow.add_conditional_edges(
        "visualize_web_node",
        visualize_web_data_process.should_continue,
        {
            "continue" : "tool_node",
            "end" : END
        }
    )
    workflow.add_edge("tool_node", "visualize_web_node")


    # visualize_upload_data process
    workflow.add_conditional_edges(
        "visualize_upload_node",
        visualize_upload_data_process.should_continue,
        {
            "continue" : "visualize_upload_node",
            "end" : END
        }
    )

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
    app = workflow.compile(checkpointer=limited_memory)
    
    return app