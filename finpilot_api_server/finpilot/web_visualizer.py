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
    def __init__(self):

        # web search tool
        web_search_tool = TavilySearchResults(max_results=3)

        # python code interpreter
        repl = PythonREPL()
        @tool
        def python_repl(
            code : Annotated[str, "The Python code to execute to generate your chart."]
        ):
            """
            Use this to execute python code.

            If you want to see the output of a value, you should print it out with 'print(...)'. chart labels should be written in English.

            This is visible to the user.

            Please make the chart and save in './charts' folder.
            """

            try : 
                result = repl.run(code)
            except BaseException as e:
                return f"Failed to execute. Error : {repr(e)}"
            
            result_str = f"Successfully executed: \n```python\n{code}\n```Stdout: {result}"

            return (
                result_str + "\n\nIf you have completed all tasks, repond with FINAL ANSWER."
            )

        self.tools = [web_search_tool, python_repl]
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
        
        result = self.llm_with_tools.invoke(state["messages"])
        state["generation"] = result.content
        state["messages"] = add_messages(state["messages"], result)

        return state
    
    def should_continue(self, state):
        messages = state["messages"]
        last_message = messages[-1]
        if not last_message.tool_calls:
            return "end"
        else:
            return "continue"