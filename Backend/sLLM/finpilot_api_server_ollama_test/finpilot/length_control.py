############################# Import Modules #############################
# (ChatOpenAI 관련 모듈은 더 이상 사용하지 않습니다)
from langchain_core.output_parsers import StrOutputParser

# 메시지 처리 모듈
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages

import os

from langchain_core.prompts import ChatPromptTemplate
from langserve import RemoteRunnable

class LengthControlProcess:
    def __init__(self):
        # 원격 LLM 엔드포인트 사용 (ChatOpenAI 대신 RemoteRunnable 사용)
        llm = RemoteRunnable("https://termite-upward-monthly.ngrok-free.app/llm/")

        prompt = ChatPromptTemplate.from_template(
            "입력에 따라 문장 요약 또는 확장. 요약 및 확장 명령은 출력에 표시하지 말 것.:\n{input}"
        )


        self.length_controller =  prompt | llm | StrOutputParser()

    async def length_control_node(self, state):
        """
        주어진 텍스트를 요약하거나 확장합니다.

        Args:
            state (dict): 현재 그래프 상태를 포함하는 딕셔너리

        Returns:
            state (dict): 'generation' 키에 LLM 생성 결과를 추가한 그래프 상태
        """
        print("[Graph Log] LENGTH CONTROL ...")

        question = state.get("question", "")
        updated_messages = add_messages(state["messages"], HumanMessage(content=question))
        state["messages"] = updated_messages
        # 원격 LLM을 호출하여 결과를 가져옵니다.
        generation = await self.length_controller.ainvoke({"input": question})

        state["generation"] = generation
        updated_messages = add_messages(state["messages"], AIMessage(content=generation))
        state["messages"] = updated_messages

        return state
