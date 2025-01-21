############################### Import Modules ###############################
# import os

# # Define Tools
import pandas as pd
# from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# # Define Nodes
# from langgraph.graph.message import add_messages
# from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage

# # Define Agent
from langgraph.prebuilt import create_react_agent
# from datetime import datetime

from pathlib import Path

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


class InnerVisualizerProcess:
    def __init__(self, session_id:str):

        self.DATA_DIR = Path(os.getcwd()) / 'data' / f"{session_id}"
        print(f"[Server Log] FIND DATA IN PATH : {self.DATA_DIR}")
        
        files = os.listdir(self.DATA_DIR)
        csv_files = [file for file in files if file.endswith(".csv")]
        print(f"[Server Log] CSV FILES IN DIR ARE : {len(csv_files)}")
        self.data_path = self.DATA_DIR / csv_files[0]
        print(f"[Server Log] CSV DATA PATH : {self.data_path}")

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

        # @tool
        # def analyze_data(query : str):
        #     """
        #     저장된 데이터를 pandas_agent로 분석하고 분석한 내용을 시각화 하는 코드를 생성합니다.
        #     """

        #     # data_path = self.DATA_DIR / "stock_data.csv"
        #     data = pd.read_csv(self.data_path)
        #     print(f"[Graph Log] FETCH DATA FROM PATH : {self.data_path}")

        #     custom_prefix = f"""
        #         You are very smart analyst with datafram.

        #         Please analyze the data in various perspective to fine valuable insight.

        #         You shoould always make the greatest output with accurate metrics and graph.

        #         Write code to visualize the analysis you have conducted.

        #         data path : {self.data_path}
        #     """

        #     pandas_agent = create_pandas_dataframe_agent(
        #         ChatOpenAI(
        #             model="gpt-4o", 
        #             api_key=os.getenv("OPENAI_API_KEY")
        #         ),
        #         [data],
        #         verbose=True,
        #         # verbose=False,
        #         agent_type = AgentType.OPENAI_FUNCTIONS,
        #         allow_dangerous_code=True,
        #         prefix = custom_prefix
        #     )

        #     result = pandas_agent.invoke(query)

        #     return result

        # self.tools = [analyze_data, python_repl_tool]
        # self.tools = [python_repl_tool]
        
        # self.tool_node = ToolNode(self.tools)

        ################################ Define AGent ################################

        # data_path = self.DATA_DIR / "stock_data.csv"
        data = pd.read_csv(self.data_path)
        print(f"[Graph Log] FETCH DATA FROM PATH : {self.data_path}")

        custom_prefix = f"""
        You are an exceptional data analyst with datafram. Your mission is to adhere to the following tasks while analyzing data, generating charts, and saving them:

        1. Visualize the provided data in the format requested by the user and save the chart in the ./charts/{session_id}/ folder.
        2. Analyze the provided data not only in the way requested by the user but also from various perspectives to uncover valuable insights.
        3. Visualize the discovered insights and save the charts in the ./charts/{session_id}/ folder.
        
        Always explain your reasoning clearly and support your conclusions with specific metrics. Conduct thorough analysis while maintaining objectivity.

        data path : {self.data_path}
        """

        self.pandas_agent = create_pandas_dataframe_agent(
            ChatOpenAI(
                model="gpt-4o", 
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            [data],
            extra_tools=[python_repl_tool],
            verbose=True,
            # verbose=False,
            agent_type = AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True,
            prefix = custom_prefix
        )

        # analyst_prompt = f"""
        # 당신은 뛰어난 데이터 분석가입니다. 아래 임무를 지키면서, 데이터를 분석하고, 차트를 생성 및 저장해야 합니다.
        # 당신의 임무는:
        # 1. 주어진 데이터에 대해 사용자가 원하는 형태의 시각화 하여 './charts/{session_id}/' 폴더에 저장하는 것.
        # 2. 주어진 데이터에 대해 사용자가 원하는 시각 뿐만 아닌 다양한 시각으로 분석하고 이에 대한 인사이트를 발견하는 것.
        # 3. 발견한 Insight에 대해 시각화 하여 './charts/{session_id}/' 폴더에 저장하는 것.

        # 당신의 추론을 항상 명확히 설명하고, 특정 지표로 결론을 뒷받침하세요.

        # 분석을 철저히 하되, 객관성을 유지하는 것을 잊지 마세요."""

        # llm = ChatOpenAI(
        #     model="gpt-4o", 
        #     api_key=os.getenv("OPENAI_API_KEY")
        # )

        # self.analyst_agent = create_react_agent(
        #     llm, 
        #     [analyze_data, python_repl_tool], 
        #     state_modifier = analyst_prompt
        # )
    
    def inner_visualizer_node(self, state):
        question = state["question"]
        state["messages"] = add_messages(state["messages"], HumanMessage(content=question))

        result = self.pandas_agent.invoke(
            input={
                "input" : {"messages" : [
                        HumanMessage(
                            content = f"""
                                Analyze given data and Visualize Chart,

                                Human Message : {question}
                            """
                        )
                    ]
                }
            }
        )
        # print(f"[Graph Log] Current Data Analize message : {result}")
        state["messages"] = add_messages(state["messages"], AIMessage(content=result['output']))
        state["generation"] = state["messages"][-1]

        return state

    
    # def inner_visualizer_node(self, state):
    #     question = state["question"]
    #     state["messages"] = add_messages(state["messages"], HumanMessage(content=question))

    #     result = self.analyst_agent.invoke(
    #         {"messages" : [
    #             HumanMessage(
    #                 content = f"""
    #                     Analyze given data and Visualize Chart,

    #                     Human Message : {question}
    #                 """
    #             )
    #         ]}
    #     )
    #     state["messages"] = add_messages(state["messages"], result['messages'])
    #     state["generation"] = state["messages"][-1]

    #     return state


# class InnerVisualizerProcess:

#     def __init__(self, session_id):
#         self.DATA_DIR = Path(os.getcwd()) / 'data' / f"{session_id}" # 데이터 저장용 디렉토리
#         print(f"[Server Log] FIND DATA IN PATH : {self.DATA_DIR}")
        
#         files = os.listdir(self.DATA_DIR)
#         csv_files = [file for file in files if file.endswith(".csv")]
#         print(f"[Server Log] CSV FILES IN DIR ARE : {len(csv_files)}")
#         self.data_path = self.DATA_DIR / csv_files[0]
#         print(f"[Server Log] CSV DATA PATH : {self.data_path}")
    

#         @tool
#         def analyze_data(query : str):
#             """
#             저장된 데이터를 pandas_agent로 분석하고 분석한 내용을 시각화 합니다.
#             """

#             # data_path = self.DATA_DIR / "stock_data.csv"
#             data = pd.read_csv(self.data_path)

#             custom_prefix = f"""
#                 You are very smart analyst with datafram.

#                 Please analyze the data in various perspective to fine valuable insight.

#                 You shoould always make the greatest output with accurate metrics and graph.

#                 data path : {self.data_path}
#             """

#             pandas_agent = create_pandas_dataframe_agent(
#                 ChatOpenAI(
#                     model="gpt-4o", 
#                     api_key=os.getenv("OPENAI_API_KEY")
#                 ),
#                 [data],
#                 verbose=True,
#                 # verbose=False,
#                 agent_type = AgentType.OPENAI_FUNCTIONS,
#                 allow_dangerous_code=True,
#                 prefix = custom_prefix
#             )

#             result = pandas_agent.invoke(query)

#             return result

#         @tool
#         def chart_generator(query:str):
#             """
#             이 도구는 create_pandas_dataframe_agent를 사용하여 차트를 생성하고 차트를 /charts 폴더에 저장합니다.
#             """

#             # data = pd.read_csv(self.DATA_DIR / "stock_data.csv")
#             data = pd.read_csv(self.data_path)
#             custom_prefix = f"""
#                 Please make the chart and save in './charts' folder.
#                 data path is '{self.data_path}'
#             """

#             agent = create_pandas_dataframe_agent(
#                 ChatOpenAI(
#                     model="gpt-4o", 
#                     api_key=os.getenv("OPENAI_API_KEY")
#                 ),
#                 [data],
#                 verbose=True,
#                 # verbose=False,
#                 agent_type=AgentType.OPENAI_FUNCTIONS,
#                 allow_dangerous_code=True,
#                 prefix = custom_prefix
#             )

#             result = agent.invoke(query)

#             return result
    
        
#         today = datetime.today().date().strftime('%Y-%m-%d')

#         analyst_prompt = f"""
#         오늘은 {today}입니다. 

#         당신은 뛰어난 데이터 분석가입니다. 아래 임무를 지키면서, 데이터를 분석하고, 차트를 생성 및 저장해야 합니다.
#         당신의 임무는:
#         1. 주어진 데이터에 대해 사용자가 원하는 형태의 시각화 하여 /charts 폴더에 저장하는 것.
#         2. 주어진 데이터에 대해 사용자가 원하는 시각 뿐만 아닌 다양한 시각으로 분석하고 이에 대한 인사이트를 발견하는 것.
#         3. 발견한 Insight에 대해 시각화 하여 /charts 폴더에 저장하는 것.

#         당신의 추론을 항상 명확히 설명하고, 특정 지표로 결론을 뒷받침하세요.

#         분석을 철저히 하되, 객관성을 유지하는 것을 잊지 마세요."""

#         llm = ChatOpenAI(
#             model="gpt-4o", 
#             api_key=os.getenv("OPENAI_API_KEY")
#         )

#         self.analyst_agent = create_react_agent(
#             llm, 
#             [analyze_data, chart_generator], 
#             state_modifier = analyst_prompt
#         )
    
#     def inner_visualizer_node(self, state : dict):
#         question = state["question"]
#         state["messages"] = add_messages(state["messages"], HumanMessage(content=question))

#         result = self.analyst_agent.invoke(
#             {"messages" : [
#                 HumanMessage(
#                     content = f"""
#                         Analyze given data and Visualize Chart,

#                         Human Message : {question}
#                     """
#                 )
#             ]}
#         )
#         state["messages"] = add_messages(state["messages"], result['messages'])
#         state["generation"] = state["messages"][-1]

#         return state