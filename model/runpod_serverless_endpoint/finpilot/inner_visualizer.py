############################### Import Modules ###############################
import os

# Define Tools
import pandas as pd
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Define Nodes
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

# Define Agent
from langgraph.prebuilt import create_react_agent
from datetime import datetime

from pathlib import Path





class InnerVisualizerProcess:

    def __init__(self):
        self.DATA_DIR = Path(os.getcwd()) / 'data' # 데이터 저장용 디렉토리

        @tool
        def analyze_data(query : str):
            """
            저장된 데이터를 pandas_agent로 분석하고 분석한 내용을 시각화 합니다.
            """

            data_path = self.DATA_DIR / "stock_data.csv"
            data = pd.read_csv(data_path)

            custom_prefix = f"""
                You are very smart analyst with datafram.

                Please analyze the data in various perspective to fine valuable insight.

                You shoould always make the greatest output with accurate metrics and graph.

                data path : {data_path}
            """

            pandas_agent = create_pandas_dataframe_agent(
                ChatOpenAI(
                    model="gpt-4o", 
                    api_key=os.getenv("OPENAI_API_KEY")
                ),
                [data],
                verbose=True,
                # verbose=False,
                agent_type = AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True,
                prefix = custom_prefix
            )

            result = pandas_agent.invoke(query)

            return result

        @tool
        def chart_generator(query:str):
            """
            이 도구는 create_pandas_dataframe_agent를 사용하여 차트를 생성하고 차트를 /charts 폴더에 저장합니다.
            """

            data = pd.read_csv(self.DATA_DIR / "stock_data.csv")
            custom_prefix = """
                Please make the chart and save in './charts' folder.
                data path is './data/stock_data.csv'
            """

            agent = create_pandas_dataframe_agent(
                ChatOpenAI(
                    model="gpt-4o", 
                    api_key=os.getenv("OPENAI_API_KEY")
                ),
                [data],
                verbose=True,
                # verbose=False,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True,
                prefix = custom_prefix
            )

            result = agent.invoke(query)

            return result
        
        today = datetime.today().date().strftime('%Y-%m-%d')

        analyst_prompt = f"""
        오늘은 {today}입니다. 

        당신은 뛰어난 데이터 분석가입니다. 아래 임무를 지키면서, 데이터를 분석하고, 차트를 생성 및 저장해야 합니다.
        당신의 임무는:
        1. 주어진 데이터에 대해 사용자가 원하는 형태의 시각화 하여 /charts 폴더에 저장하는 것.
        2. 주어진 데이터에 대해 사용자가 원하는 시각 뿐만 아닌 다양한 시각으로 분석하고 이에 대한 인사이트를 발견하는 것.
        3. 발견한 Insight에 대해 시각화 하여 /charts 폴더에 저장하는 것.

        당신의 추론을 항상 명확히 설명하고, 특정 지표로 결론을 뒷받침하세요.

        분석을 철저히 하되, 객관성을 유지하는 것을 잊지 마세요."""

        llm = ChatOpenAI(
            model="gpt-4o", 
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.analyst_agent = create_react_agent(
            llm, 
            [analyze_data, chart_generator], 
            state_modifier = analyst_prompt
        )
    
    def get_inner_visualizer_node(self):
        def inner_visualizer_node(state : dict):
            question = state["question"]
            state["messages"] = add_messages(state["messages"], HumanMessage(content=question))

            result = self.analyst_agent.invoke(
                {"messages" : [
                    HumanMessage(
                        content = f"""
                            Analyze given data and Visualize Chart,

                            Human Message : {question}
                        """
                    )
                ]}
            )
            print("="*100)
            print(result)
            print("="*100)
            state["messages"] = add_messages(state["messages"], result['messages'])

            return state
        
        return inner_visualizer_node