############################### Import Modules ###############################
from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
# from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from IPython.display import Image

from finpilot.writer import retrieve_node, write_node, filter_documents_node, transform_query_node, web_search_node
from finpilot.writer import decide_write_or_rewrite_query, decide_to_retrieve_or_web_search, decide_to_regenerate_or_rewrite_query_or_end
from finpilot.text_magician import text_magician_node
from finpilot.web_visualizer import web_visualizer_node, tool_node
from finpilot.web_visualizer import should_continue
from finpilot.inner_visualizer import inner_visualizer_node
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
        
        self.workflow = StateGraph(State)

        ################## Add Nodes ##################

        ## writer
        self.workflow.add_node("retriever", retrieve_node)
        self.workflow.add_node("filter_documents", filter_documents_node)
        self.workflow.add_node("writer", write_node)
        self.workflow.add_node("transform_query", transform_query_node)
        self.workflow.add_node("web_search", web_search_node)

        ## text_magician
        self.workflow.add_node("text_magician", text_magician_node)

        ## web_visualizer
        self.workflow.add_node("web_visualizer", web_visualizer_node)
        self.workflow.add_node("tool", tool_node)

        ## inner_visualizer
        self.workflow.add_node("inner_visualizer", inner_visualizer_node)


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
            decide_write_or_rewrite_query,
            {
                "writer" : "writer",
                "transform_query" : "transform_query"
            },
        )
        self.workflow.add_conditional_edges(
            "transform_query",
            decide_to_retrieve_or_web_search,
            {
                "retriever" : "retriever",
                "web_search" : "web_search"
            }
        )
        self.workflow.add_edge("web_search", "writer")
        self.workflow.add_conditional_edges(
            "writer",
            decide_to_regenerate_or_rewrite_query_or_end,
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
            should_continue,
            {
                "continue" : "tool",
                "end" : END
            }
        )
        self.workflow.add_edge("tool", "web_visualizer")


        # inner_visualizer process
        self.workflow.add_edge("inner_visualizer", END)


        ################## Compile Workflow ##################
        self.app = self.workflow.compile()



    def architecture(self):
        try:
            print(Image(self.app.get_graph(xray=True).draw_mermaid_png()))
        except Exception:
            pass
    


    def invoke(self, question):
        inputs = {"question" : question}
        
        result = self.app.invoke(inputs)
        
        return result['generation']