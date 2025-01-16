from langgraph.checkpoint.memory import MemorySaver

class LimitedMemorySaver(MemorySaver):
    def __init__(self, capacity=10):
        super().__init__()
        self.capacity = capacity
    
    def save(self, message):
        # get current messages
        current_messages = self.get_all()
        # add new message
        current_messages.append(message)
        # Remain recent 10 messages
        if len(current_messages) > self.capacity:
            current_messages = current_messages[-self.capacity:]
        self.set_all(current_messages)