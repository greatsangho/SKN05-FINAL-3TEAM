################################ Import Modules ################################
import os
from config.secret_keys import OPENAI_API_KEY, USER_AGENT, TAVILY_API_KEY
from pathlib import Path

# Define Tools
from typing import Annotated
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool

# Define Agent
from langchain_openai import ChatOpenAI

# Define Node
from langgraph.prebuilt import ToolNode

# Define Edges
from langgraph.prebuilt import tools_condition
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

# Prompts
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages









################################ Directory Setting ################################
DATA_DIR = Path(os.getcwd()) / 'data' # 데이터 저장용 디렉토리
CHART_DIR = Path(os.getcwd()) / 'charts' # 차트 저장용 디엑토리










################################ Set Environment ################################
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
os.environ['TAVILY_API_KEY'] = TAVILY_API_KEY
os.environ['USER_AGENT'] = USER_AGENT










################################ Define Tools ################################
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

tools = [web_search_tool, python_repl]








################################ Define AGent ################################
llm = ChatOpenAI(
    model = "gpt-4o"
)
llm_with_tools = llm.bind_tools(tools)









################################ Define Nodes ################################
def web_visualizer_node(state):
    question = state["question"]
    updated_messages = add_messages(state["messages"], HumanMessage(content=question))
    state["messages"] = updated_messages
    
    result = llm_with_tools.invoke(state["messages"])
    state["generation"] = result.content
    state["messages"] = add_messages(state["messages"], result)

    return state

tool_node = ToolNode(tools)









################################ Define Conditional Edge Function ################################
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


