############################### Import Modules ###############################
import pandas as pd
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.messages import AIMessage
from pathlib import Path
import os
from typing import Annotated
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages


class InnerVisualizerProcess:
    def __init__(self, session_id:str):
        try:
            self.DATA_DIR = Path(os.getcwd()) / 'data' / f"{session_id}"
            # print(f"[Server Log] FIND DATA IN PATH : {self.DATA_DIR}")
            
            files = os.listdir(self.DATA_DIR)
            csv_files = [file for file in files if file.endswith(".csv")]
            # print(f"[Server Log] CSV FILES IN DIR ARE : {len(csv_files)}")
            self.data_path = self.DATA_DIR / csv_files[0]
            # print(f"[Server Log] CSV DATA PATH : {self.data_path}")

            data = pd.read_csv(self.data_path)
            # print(f"[Graph Log] FETCH DATA FROM PATH : {self.data_path}")
        except : 
            self.DATA_DIR = "tmp/"
            self.data_path = "tmp.csv"
            data = pd.DataFrame()
            # print(f"[Server Log] No CSV FILE. SET TEMP PATH.")

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

        ################################ Define AGent ################################

        

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