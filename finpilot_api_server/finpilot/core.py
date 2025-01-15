############################### Import Modules ###############################
from finpilot.workflow import get_application

class FinPilot:
    def __init__(self):
        self.app = get_application()
    
    def invoke(self, question, session_id):
        inputs = {"question" : question}

        config = {
            "configurable" : {"thread_id" : session_id}
        }
        
        result = self.app.invoke(inputs, config)
        
        return result['generation']