############################### Import Modules ###############################
from finpilot.workflow import get_application
from langgraph.checkpoint.memory import MemorySaver

class FinPilot:
    def __init__(self, memory : MemorySaver):
        self.app = get_application(memory=memory)
    
    def invoke(self, question, session_id):
        inputs = {"question" : question}

        config = {
            "configurable" : {"thread_id" : session_id}
        }
        
        result = self.app.invoke(inputs, config)
        
        return result['generation']