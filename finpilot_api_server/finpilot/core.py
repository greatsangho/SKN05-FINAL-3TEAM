############################### Import Modules ###############################
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


class FinPilot:
    def __init__(self):
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
        
        self.workflow = StateGraph(State)

        writer_process = WriterProcess()
        text_magician_process = TextMagicianProcess()
        web_visualizer_process = WebVisualizerProcess()
        inner_visualizer_process = InnerVisualizerProcess()

        ################## Add Nodes ##################

        ## writer
        self.workflow.add_node("retriever", writer_process.get_retrieve_node())
        self.workflow.add_node("filter_documents", writer_process.get_filter_documents_node())
        self.workflow.add_node("writer", writer_process.get_write_node())
        self.workflow.add_node("transform_query", writer_process.get_transform_query_node())
        self.workflow.add_node("web_search", writer_process.get_web_search_node())

        ## text_magician
        self.workflow.add_node("text_magician", text_magician_process.get_text_magician_node())

        ## web_visualizer
        self.workflow.add_node("web_visualizer", web_visualizer_process.get_web_visualizer_node())
        self.workflow.add_node("tool", web_visualizer_process.get_tool_node())

        ## inner_visualizer
        self.workflow.add_node("inner_visualizer", inner_visualizer_process.get_inner_visualizer_node())


        ################## add edges ##################
        ## Route Question
        self.workflow.add_conditional_edges(
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
        self.workflow.add_edge("retriever", "filter_documents")
        self.workflow.add_conditional_edges(
            "filter_documents",
            writer_process.get_decide_write_or_rewrite_query(),
            {
                "writer" : "writer",
                "transform_query" : "transform_query"
            },
        )
        self.workflow.add_conditional_edges(
            "transform_query",
            writer_process.get_decide_to_retrieve_or_web_search(),
            {
                "retriever" : "retriever",
                "web_search" : "web_search"
            }
        )
        self.workflow.add_edge("web_search", "writer")
        self.workflow.add_conditional_edges(
            "writer",
            writer_process.get_decide_to_regenerate_or_rewrite_query_or_end(),
            {
                "not supported" : "writer",
                "useful" : END,
                "not useful" : "transform_query"
            }
        )

        # text_magician process
        self.workflow.add_edge("text_magician", END)


        # web_visualizer process
        self.workflow.add_conditional_edges(
            "web_visualizer",
            web_visualizer_process.get_should_continue(),
            {
                "continue" : "tool",
                "end" : END
            }
        )
        self.workflow.add_edge("tool", "web_visualizer")


        # inner_visualizer process
        self.workflow.add_edge("inner_visualizer", END)


        ################## Compile Workflow ##################
        self.app = self.workflow.compile(checkpointer=memory)
    


    def invoke(self, question, session_id):
        inputs = {"question" : question}

        config = {
            "configurable" : {"thread_id" : session_id}
        }
        
        result = self.app.invoke(inputs, config)
        
        return result['generation']