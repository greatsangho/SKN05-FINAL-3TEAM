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
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph.message import add_messages


class VisualizeUploadDataProcess:
    def __init__(self):
        repl = PythonREPL()
        def python_repl(
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
        
        self.python_repl_tool = tool(python_repl)
   
    
    async def visualize_node(self, state):
        question = state["question"]
        session_id = state["session_id"]

        DATA_DIR = Path(os.getcwd()) / 'data' / f'{session_id}'
        files = os.listdir(DATA_DIR)
        csv_files = [file for file in files if file.endswith(".csv")]
        csvfile = csv_files[0]
        data_path = DATA_DIR / csvfile
        data = pd.read_csv(data_path)

        custom_prefix = f"""
            You are an exceptional data analyst with datafram. Your mission is to adhere to the following tasks while analyzing data, generating charts, and saving them:

            1. Visualize the provided data in the format requested by the user and save the chart in the ./charts/{session_id}/ folder.
            2. Analyze the provided data not only in the way requested by the user but also from various perspectives to uncover valuable insights.
            3. Visualize the discovered insights and save the charts in the ./charts/{session_id}/ folder.
            
            Always explain your reasoning clearly and support your conclusions with specific metrics. Conduct thorough analysis while maintaining objectivity.

            data path : {data_path}
        """

        self.pandas_agent = create_pandas_dataframe_agent(
            ChatOpenAI(
                model="gpt-4o", 
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            [data],
            extra_tools=[self.python_repl_tool],
            verbose=True,
            agent_type = AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True,
            prefix = custom_prefix
        )

        updated_messages = add_messages(state["messages"], HumanMessage(content=question))
        state["messages"] = updated_messages

        result = await self.pandas_agent.ainvoke(
            input={
                "input" : {"messages" : updated_messages
                }
            }
        )
        state["messages"] = add_messages(state["messages"], AIMessage(content=result['output']))
        state["generation"] = state["messages"][-1]
        state["source"] = csvfile

        return state
    
    async def should_continue(self, state):
        session_id = state["session_id"]
        folder_path = f"./charts/{session_id}/"

        print("[Graph Log] DECISION CONTINUE OR NOT ...")
        if len(os.listdir(folder_path)) != 0:
            print("[Graph Log] DECISION : END")
            return "end"
        else:
            print("[Graph Log] DECISION : CONTINUE")
            return "continue"