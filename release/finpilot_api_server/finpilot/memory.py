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
        print(current_messages["documents"])
        del current_messages["documents"]
        print(current_messages["documents"])
        # add new message
        current_messages.append(message)
        # Remain recent 10 messages
        if len(current_messages) > self.capacity:
            current_messages = current_messages[-self.capacity:]
        self.set_all(current_messages)
    
    # def put(self, config, checkpoint, metadata, new_versions=None):
    #     # 필터링하여 제외할 키들을 제거
    #     if "__start__" in checkpoint["channel_values"]:
    #         print(checkpoint["channel_values"]["__start__"])
    #         checkpoint["channel_values"]["__start__"]["documents"] = []
    #         print(checkpoint["channel_values"]["__start__"]["documents"])

    #     # 부모 클래스의 put 메서드 호출 (기존 저장 로직 유지)
    #     return super().put(config, checkpoint, metadata, new_versions)
    
    def __getstate__(self):
        """직렬화 상태 반환"""
        state = self.__dict__.copy()
        state['messages'] = self.get_all()  # 메시지 상태 포함
        return state

    def __setstate__(self, state):
        """직렬화 상태 복원"""
        self.__dict__.update(state)
        self.set_all(state.get('messages', []))