############################# Import Modules #############################
import os
import numpy as np
import asyncio
from joblib import Parallel, delayed

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langserve import RemoteRunnable
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document
from langchain_chroma import Chroma

# 헬퍼 함수: 문서를 Document 객체로 변환
def cvt_2_doc(doc):
    return Document(
        page_content=doc["content"],
        metadata={"source": doc["url"]}
    )

# StructuredLLMWrapper를 callable하게 만들기 위한 구현
class StructuredLLMWrapper:
    def __init__(self, llm, model):
        self.llm = llm
        self.model = model

    async def ainvoke(self, input_):
        raw_output = await self.llm.ainvoke(input_)
        try:
            return self.model.parse_raw(raw_output)
        except Exception:
            return self.model.parse_obj(raw_output)

    def __call__(self, input_):
        return self.ainvoke(input_)

    def __ror__(self, other):
        # 파이프라인 체인에서 다른 Runnable과 결합 가능하도록 ComposedWrapper 반환
        return ComposedWrapper(other, self)
'''
from langchain_core.prompts import ChatPromptTemplate
from langserve import RemoteRunnable
from langchain_core.output_parsers import StrOutputParser

class GradeProcess:
    def __init__(self):
        # 원격 LLM 엔드포인트 사용 (ChatOpenAI 대신 RemoteRunnable 이용)
        llm = RemoteRunnable("https://termite-upward-monthly.ngrok-free.app/llm/")
        
        # 평가를 위한 시스템 메시지와 사용자 메시지 정의
        grader_system_prompt = (
            "당신은 검색된 문서와 사용자 질문의 관련성을 평가하는 평가자입니다. "
            "문서에 관련 정보가 포함되어 있다면 'yes', 그렇지 않다면 'no'로 응답하세요."
        )
        grader_human_prompt = "Retreived documents : \n\n{documents}\n\nUser question : {question}"
        
        # ChatPromptTemplate을 from_messages 메서드를 사용해 생성
        grade_prompt = ChatPromptTemplate.from_messages([
            ("system", grader_system_prompt),
            ("human", grader_human_prompt)
        ])
        
        # 프롬프트, 원격 LLM, 후처리기를 파이프라인 체인으로 연결
        self.grade_controller = grade_prompt | llm | StrOutputParser()

    async def grade(self, documents: str, question: str) -> str:
        """
        평가(grade)를 실행합니다.

        Args:
            documents (str): 평가에 사용될 문서 내용
            question (str): 사용자 질문

        Returns:
            str: LLM에 의해 출력된 평가 결과 (예: "yes" 혹은 "no")
        """
        input_data = {"documents": documents, "question": question}
        return await self.grade_controller.ainvoke(input_data)
'''
class ComposedWrapper:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    async def ainvoke(self, input_):
        result = await self.left.ainvoke(input_)
        return await self.right.ainvoke(result)

class ParagraphProcess:
    def __init__(self, vector_store: Chroma):
        # vector_store는 즉시 저장하지만, heavy initialization은 lazy init으로 함
        self.retrieve = vector_store.as_retriever(dynamic_update=True)
        self._initialized = False  # lazy init 플래그
        # 아래 속성들은 _lazy_init에서 초기화됩니다.
        self.retrieval_grader = None
        self.writer = None
        self.hallucination_grader = None
        self.answer_grader = None
        self.query_improver = None
        self.web_search_tool = None

    async def _lazy_init(self):
        # 이미 초기화되었다면 다시 실행하지 않음
        if self._initialized:
            return

        # Remote LLM (여기서는 OpenLLM 엔드포인트) 설정
        llm = RemoteRunnable("https://termite-upward-monthly.ngrok-free.app/llm/")

        # 내부에서만 사용하는 Pydantic 모델 정의 (lazy init 내에서 실행)
        class GradeDocuments(BaseModel):
            """
            검색된 문서와 사용자 질문의 관련성을 평가하는 모델.
            """
            relevance_score: str = Field(
                description="Document are relevant to the question, 'yes' or 'no'"
            )

        class GradeHallucination(BaseModel):
            """
            LLM 생성 결과가 제공된 사실에 기반하는지 평가하는 모델.
            """
            hallucination_score: str = Field(
                description="Answer is grounded in the facts, 'yes' or 'no'"
            )

        class AnswerGrader(BaseModel):
            """
            생성된 답변이 질문을 해결하는지 평가하는 모델.
            """
            answer_score: str = Field(
                description="Answer addresses the question, 'yes' or 'no'"
            )

        # # StructuredLLMWrapper를 사용하여 기존 with_structured_output 대신 구성
        # grader_structured_llm = StructuredLLMWrapper(llm, GradeDocuments)
        # hallucination_structured_llm = StructuredLLMWrapper(llm, GradeHallucination)
        # answer_structured_llm = StructuredLLMWrapper(llm, AnswerGrader)

        # 시스템 프롬프트 정의 (각 평가 역할에 맞게)
        grader_system_prompt = """
            You are a grader assessing relevance of a retrieved document to a user question.
            If the document contains keyword(s) or semantic meaning related to the question, respond with 'yes', otherwise 'no'.
        """
        hallucination_system_prompt = """
            You are a grader assessing whether an LLM generation is supported by a set of retrieved facts.
            Respond with 'yes' if it is grounded in the facts, otherwise 'no'.
        """
        answer_system_prompt = """
            You are a grader assessing whether an answer addresses and resolves the question.
            Respond with 'yes' if it does, otherwise 'no'.
        """
        improve_system_prompt = """
            You are a question re-writer that optimizes an input question for vectorstore retrieval.
            Analyze the input and produce an improved version.
        """
        grader_human_prompt = "Retreived documents : \n\n{documents}\n\nUser question : {question}"
        grade_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", grader_system_prompt),
                ("human", grader_human_prompt)
            ]
        )
        # grade_prompt = ChatPromptTemplate.from_messages(
        #     [
        #         ("system", grader_system_prompt),
        #         ("human", "Retreived documents : \n\n{documents}\n\nUser question : {question}")
        #     ]
        # )
        write_prompt = hub.pull("rlm/rag-prompt")
        hallucination_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", hallucination_system_prompt),
                ("human", "Set of facts : \n\n{documents}\n\nLLM generation : {generation}")
            ]
        )
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", answer_system_prompt),
                ("human", "User question : \n\n{question}\n\nLLM generation : {generation}")
            ]
        )
        improve_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", improve_system_prompt),
                ("human", "Here is the initial question : \n\n{question}\nFormulate an improved question")
            ]
        )

        # 체인 구성: 프롬프트와 모델을 Runnable 체인으로 연결
        self.retrieval_grader = grade_prompt | grader_structured_llm
        self.writer = write_prompt | llm | StrOutputParser()
        self.hallucination_grader = hallucination_prompt | hallucination_structured_llm
        self.answer_grader = answer_prompt | answer_structured_llm
        self.query_improver = improve_prompt | llm
        self.web_search_tool = TavilySearchResults(k=3)

        self._initialized = True

    async def retrieve_node(self, state):
        print("[Graph Log] RETRIEVE ...")
        await self._lazy_init()  # 초기화가 필요한 경우 여기서 실행됨
        question = state["question"]
        session_id = state["session_id"]

        try:
            prev_documents = state["documents"]
            retrieved_documents = await self.retrieve.ainvoke(
                input=question,
                filter={"session_id": session_id}
            )
            documents = prev_documents + retrieved_documents
        except Exception:
            documents = await self.retrieve.ainvoke(
                input=question,
                filter={"session_id": session_id}
            )

        state["documents"] = documents
        return state

    async def write_node(self, state):
        print("[Graph Log] WRITE ...")
        await self._lazy_init()  # heavy 초기화가 완료되었는지 확인
        question = state["question"]
        documents = state["documents"]

        # 문서의 원본 URL 수집
        source = []
        for document in documents:
            source.append(document.metadata["source"])
        state["source"] = list(np.unique(source))

        updated_messages = add_messages(state["messages"], HumanMessage(content=question))
        state["messages"] = updated_messages

        generation = await self.writer.ainvoke({"context": documents, "question": question})
        state["generation"] = generation

        updated_messages = add_messages(state["messages"], AIMessage(content=generation))
        state["messages"] = updated_messages
        return state

    async def filter_documents_node(self, state):
        print("[Graph Log] FILTER DOCUMENTS ...")
        await self._lazy_init()
        question = state["question"]
        documents = state["documents"]

        filtered_docs = await self.filter_documents(question=question, documents=documents)
        state["documents"] = filtered_docs
        return state

    async def improve_query_node(self, state):
        print("[Graph Log] TRANSFORM QUERY ...")
        await self._lazy_init()
        question = state["question"]
        improved_query = await self.query_improver.ainvoke({"question": question})
        state['question'] = improved_query.content
        return state

    async def web_search_node(self, state):
        print("[Graph Log] WEB SEARCH ...")
        await self._lazy_init()
        question = state["question"]
        documents = state["documents"]

        if isinstance(question, str):
            query = question
        else:
            query = str(question.content) if hasattr(question, 'content') else str(question)

        docs = await self.web_search_tool.ainvoke({"query": query, "days": 30})
        web_results = Parallel(n_jobs=4)(delayed(cvt_2_doc)(doc) for doc in docs)
        documents.extend(web_results)
        state["documents"] = documents
        return state

    async def decide_write_or_improve_query(self, state):
        print("[Graph Log] DETERMINES 'WRITE' OR 'REWRITE QUESTION' ...")
        await self._lazy_init()
        documents = state["documents"]
        return "writer" if len(documents) >= 6 else "improve_query"

    async def decide_to_regenerate_or_rewrite_query_or_end(self, state):
        print("[Graph Log] CHECK HALLUCINATIONS ...")
        await self._lazy_init()
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = await self.hallucination_grader.ainvoke({"documents": documents, "generation": generation})
        hallucination_grade = score.hallucination_score

        if hallucination_grade == "yes":
            print("[Graph Log] DECISION : ANSWER IS GROUNDED IN DOCUMENTS")
            score = await self.answer_grader.ainvoke({"question": question, "generation": generation})
            answer_grade = score.answer_score
            if answer_grade == "yes":
                print("[Graph Log] DECISION : GENERATION ADDRESSES QUESTION")
                return "useful"
            else:
                print("[Graph Log] DECISION : GENERATION DOES NOT ADDRESS QUESTION")
                return "not useful"
        else:
            print("[Graph Log] DECISION : GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY")
            return "not supported"

    async def document_filter(self, question, doc):
        await self._lazy_init()
        score = await self.retrieval_grader.ainvoke({"question": question, "documents": doc.page_content})
        relevance_grade = score.relevance_score
        print("[Relevance Grader Log] GRADE :", "DOCUMENT RELEVANT" if relevance_grade == "yes" else "DOCUMENT NOT RELEVANT")
        return doc if relevance_grade == "yes" else None

    async def filter_documents(self, question, documents):
        tasks = [self.document_filter(question=question, doc=doc) for doc in documents]
        filtered_documents = await asyncio.gather(*tasks)
        return [doc for doc in filtered_documents if doc is not None]
