############################### Import Modules ###############################
from finpilot.workflow import create_application
# from langgraph.checkpoint.memory import MemorySaver
from finpilot.memory import LimitedMemorySaver

class FinPilot:
    def __init__(self, memory : LimitedMemorySaver):
        self.app = create_application(memory=memory)
    
    def invoke(self, question, session_id):
        inputs = {"question" : question}

        config = {
            "configurable" : {"thread_id" : session_id}
        }
        
        result = self.app.invoke(inputs, config)
        
        return result['generation']