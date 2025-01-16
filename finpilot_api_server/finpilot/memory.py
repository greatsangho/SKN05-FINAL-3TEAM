from langgraph.checkpoint.memory import MemorySaver

class LimitedMemorySaver(MemorySaver):
    def __init__(self, capacity=10):
        super().__init__()
        self.capacity = capacity
        self._messages = []  # 메시지를 저장할 내부 리스트

    def get_all(self):
        """모든 메시지를 반환"""
        return self._messages

    def set_all(self, messages):
        """메시지 리스트를 설정"""
        self._messages = messages
    
    def save(self, message):
        # get current messages
        current_messages = self.get_all()
        # add new message
        current_messages.append(message)
        # Remain recent 10 messages
        if len(current_messages) > self.capacity:
            current_messages = current_messages[-self.capacity:]
        self.set_all(current_messages)
    
    def __getstate__(self):
        """직렬화 상태 반환"""
        state = self.__dict__.copy()
        state['messages'] = self.get_all()  # 메시지 상태 포함
        return state

    def __setstate__(self, state):
        """직렬화 상태 복원"""
        self.__dict__.update(state)
        self.set_all(state.get('messages', []))