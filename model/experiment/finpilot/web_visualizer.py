################################ Import Modules ################################
import os

# Define Tools
from typing import Annotated
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool

# Define Agent
from langchain_openai import ChatOpenAI

# Define Node
from langgraph.prebuilt import ToolNode

# Prompts
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages



class WebVisualizerProcess:
    def __init__(self, session_id:str):

        # web search tool
        web_search_tool = TavilySearchResults(max_results=3)

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