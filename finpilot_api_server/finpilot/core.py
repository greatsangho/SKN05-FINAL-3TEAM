############################### Import Modules ###############################
from finpilot.workflow import create_application
# from langgraph.checkpoint.memory import MemorySaver
from finpilot.memory import LimitedMemorySaver
from langchain_community.vectorstores import FAISS

class FinPilot:
    def __init__(self, memory : LimitedMemorySaver, vector_store : FAISS, session_id:str):
        self.app = create_application(memory=memory, vector_store=vector_store, session_id=session_id)
    
    def invoke(self, question, session_id):
        inputs = {"question" : question}

        config = {
            "configurable" : {"thread_id" : session_id},
            "recursion_limit" : 40
        }
        
        result = self.app.invoke(inputs, config)
        
        return result['generation']