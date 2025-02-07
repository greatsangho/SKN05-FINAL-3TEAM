################################ Import Modules ################################
import os
import numpy as np
import json

# Define Tools
from typing import Annotated
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool

# Define Agent
from langchain_openai import ChatOpenAI

# Define Node
from langgraph.prebuilt import ToolNode
from datetime import datetime

# Prompts
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph.message import add_messages



class VisualizeWebDataProcess:
    def __init__(self):
        # web search tool
        tavily_search_tool = TavilySearchResults(max_results=3)
        @tool
        async def web_search_tool(input):
            """
            Use this tool for search information or data from web

            Returns:
                web_search_results (List[dict]) : list of dict that contains web search results
                source (List[str]) : url source of searched data
            """
            web_results = await tavily_search_tool.ainvoke(input)
            urls = []
            for web_result in web_results:
                urls.append(web_result["url"])
            urls = list(np.unique(urls))

            return {
                "web_search_results" : web_results,
                "source" : urls
            }

        # python code interpreter
        repl = PythonREPL()
        @tool
        def python_repl_tool(
            code : Annotated[str, "The Python code to execute to generate and save your chart."]
        ):
            """
            Use this tool to execute Python code and generate the desired results.

            Write Python code that generates a graph and saves the graph in to image.

            If the specified folder does not exist, create the folder at the given path.

            Follow the requirements below to write the code:

            1. Save the generated graph in to image.
            2. The image format should be PNG.
            3. chart labels should be written in English.
            4. Ensure proper cleanup of resources used by Matplotlib to prevent memory leaks.
            5. use 'matplotlib.use('Agg')' for run matplotlib
            
            The result should be fully functional Python code. Add comments to explain each step of the code.
            """

            try : 
                result = repl.run(code)
            except BaseException as e:
                return f"Failed to execute. Error : {repr(e)}"
            
            result_str = f"Successfully executed: \n```python\n{code}\n```Stdout: {result}"

            return (
                result_str + "\n\nIf you have completed all tasks, repond with FINAL ANSWER."
            )

        self.tools = [web_search_tool, python_repl_tool]

        self.tool_node = ToolNode(self.tools)

        ################################ Define AGent ################################
        llm = ChatOpenAI(
            model = "gpt-4o",
            api_key = os.getenv("OPENAI_API_KEY")
        )
        self.llm_with_tools = llm.bind_tools(self.tools)
    
    async def visualize_node(self, state):
        question = state["question"]
        session_id = state["session_id"]

        if len(state["messages"]) > 0:
            if state["messages"][-1].name == "web_search_tool":
                web_search_tool_message = state["messages"][-1]
                content_str = web_search_tool_message.content
                content = json.loads(content_str)
                state["source"] = content["source"]
        
        today = datetime.today().strftime("%Y-%m-%d")

        system_prompt = f"""
            오늘은 {today} 입니다. 
            
            당신은 데이터 시각화 엔지니어 입니다. 
            당신은 사용자의 요청에 부합하는 데이터를 검색하고, 이를 바탕으로 데이터를 분석하여 시각화할 수 있는 PYthon Code를 생성 해야합니다.

            이를 위해 당신이 사용할 수 있는 도구는 다음과 같습니다.
            <도구>
            web_search_tool : 사용자의 요청에 부합하는 데이터를 검색하기 위한 '웹 검색 도구'
            python_repl_tool : 웨 검색을 통해 수집한 데이터를 시각화 할 수 있는 Python Code를 실행할 수 있는 도구
            </도구>

            다음의 지침에 따라 사용자의 요청에 따른 시각화 코드를 생성하고 실행하세요.
            <지침>
            1. 사용자의 요청에 대한 데이터를 웹 검색을 통해 수집하세요.
            2. 웹 검색을 통해 수집한 데이터를 분석하고 시각화 할 수 있는 Python Code를 생성하세요
            3. Python Code 에는 생성한 그래프 이미지를 './charts/{session_id}/' 폴더에 저장하는 Code가 포함되어야 합니다. (매우 중요)
            4. 반드시 지정한 경로에 이미지 파일을 저장하는 Python Code를 생성하세요. (경로 : './charts/{session_id}/')
            5. Python Code 에서 오류가 발생할 경우 오류를 수정하여 다시 실행하세요.
            </지침>
        """
        
        updated_messages = add_messages(state["messages"], SystemMessage(content=system_prompt))
        updated_messages = add_messages(updated_messages, HumanMessage(content=question))
        state["messages"] = updated_messages
        
        print("[Graph Log] WEB VISUALIZER AGENT WORKING ...")
        result = await self.llm_with_tools.ainvoke(state["messages"])
        state["generation"] = result.content
        state["messages"] = add_messages(state["messages"], result)

        return state
    
    async def should_continue(self, state):
        messages = state["messages"]
        last_message = messages[-1]
        folder_path = f"./charts/{state['session_id']}/"

        print("[Graph Log] DECISION CONTINUE OR NOT ...")
        if (not last_message.tool_calls) & (len(os.listdir(folder_path)) != 0):
            print("[Graph Log] DECISION : END")
            return "end"
        else:
            print("[Graph Log] DECISION : CONTINUE")
            return "continue"