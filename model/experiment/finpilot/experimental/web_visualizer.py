################################ Import Modules ################################
import os
import numpy as np
import json

# Define Tools
from typing import Annotated
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
from langchain_core.documents import Document

# Define Agent
from langchain_openai import ChatOpenAI

# Define Node
from langgraph.prebuilt import ToolNode

# Prompts
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph.message import add_messages



class WebVisualizerProcess:
    def __init__(self, session_id:str):

        # web search tool
        tavily_search_tool = TavilySearchResults(max_results=3)
        @tool
        def web_search_tool(input):
            """
            Use this tool for search information or data from web

            Returns:
                web_search_results (List[dict]) : list of dict that contains web search results
                source (List[str]) : url source of searched data
            """
            web_results = tavily_search_tool.invoke(input)
            urls = []
            for web_result in web_results:
                urls.append(web_result["url"])
            urls = list(np.unique(urls))

            return {
                "web_search_results" : web_results,
                "source" : urls
            }
            

        doc_string_template = """
            Use this tool to execute Python code and generate the desired results.

            Write Python code that generates a graph and saves the graph image in the './charts/{session_id}/' folder.

            If the specified folder does not exist, create the folder at the given path.

            Follow the requirements below to write the code:

            1. Save the generated graph image in the './charts/{session_id}/' folder.
            2. The image format should be PNG.
            3. chart labels should be written in English.
            4. Ensure proper cleanup of resources used by Matplotlib to prevent memory leaks.
            5. use 'matplotlib.use('Agg')' for run matplotlib
            
            The result should be fully functional Python code. Add comments to explain each step of the code.
        """

        # python code interpreter
        repl = PythonREPL()
        def python_repl(
            code : Annotated[str, "The Python code to execute to generate your chart."]
        ):

            try : 
                result = repl.run(code)
            except BaseException as e:
                return f"Failed to execute. Error : {repr(e)}"
            
            result_str = f"Successfully executed: \n```python\n{code}\n```Stdout: {result}"

            return (
                result_str + "\n\nIf you have completed all tasks, repond with FINAL ANSWER."
            )
        
        python_repl.__doc__ = doc_string_template.format(session_id=session_id)
        python_repl_tool = tool(python_repl)

        self.tools = [web_search_tool, python_repl_tool]
        self.tool_node = ToolNode(self.tools)

        ################################ Define AGent ################################
        llm = ChatOpenAI(
            model = "gpt-4o",
            api_key = os.getenv("OPENAI_API_KEY")
        )
        self.llm_with_tools = llm.bind_tools(self.tools)
    
    def web_visualizer_node(self, state):
        question = state["question"]

        if len(state["messages"]) > 0:
            if state["messages"][-1].name == "web_search_tool":
                web_search_tool_message = state["messages"][-1]
                content_str = web_search_tool_message.content
                content = json.loads(content_str)
                state["source"] = content["source"]
                
        updated_messages = add_messages(state["messages"], HumanMessage(content=question))
        state["messages"] = updated_messages
        
        print("[Graph Log] WEB VISUALIZER AGENT WORKING ...")
        result = self.llm_with_tools.invoke(state["messages"])
        state["generation"] = result.content
        state["messages"] = add_messages(state["messages"], result)

        return state
    
    def should_continue(self, state):
        messages = state["messages"]
        last_message = messages[-1]

        print("[Graph Log] DECISION CONTINUE OR NOT ...")
        if not last_message.tool_calls:
            print("[Graph Log] DECISION : END")
            return "end"
        else:
            print("[Graph Log] DECISION : CONTINUE")
            return "continue"