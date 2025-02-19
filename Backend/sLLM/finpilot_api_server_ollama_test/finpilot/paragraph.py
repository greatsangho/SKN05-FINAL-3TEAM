########################### Import Modules ###########################
import os
import numpy as np
import asyncio
from joblib import Parallel, delayed

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langserve import RemoteRunnable
# add optional
from typing import Optional

# Writer
from langchain import hub
from langchain_core.output_parsers import StrOutputParser

# define tools
from langchain_community.tools.tavily_search import TavilySearchResults

# define Nodes
from langchain.schema import Document

# load retriever
from langchain_chroma import Chroma

# messages
from langgraph.graph.message import add_messages

def cvt_2_doc(doc):
    return Document(
        page_content=doc["content"],
        metadata={
            "source" : doc["url"]
        }
    )

class ParagraphProcess:
    def __init__(self, vector_store : Chroma):
        # Use RemoteRunnable instead of ChatOpenAI
        llm = RemoteRunnable("https://termite-upward-monthly.ngrok-free.app/llm/")

        ########### Pydantic Models ###########
        class GradeDocuments(BaseModel):
            relevance_score: str = Field(..., description="Document is relevant to the question, 'yes' or 'no'")

        class GradeHallucination(BaseModel):
            hallucination_score: str = Field(..., description="Answer is grounded in the facts, 'yes' or 'no'")

        class AnswerGrader(BaseModel):
            answer_score: str = Field(..., description="Answer addresses the question, 'yes' or 'no'")
        ########### Response Validation ###########
        def validate_response(response: str, model: BaseModel) -> Optional[BaseModel]:
            try:
                if isinstance(response, str):
                    # 문자열 응답을 딕셔너리로 강제 변환
                    response_dict = {list(model.model_fields.keys())[0]: response}
                else:
                    response_dict = response
                return model(**response_dict)
            except Exception as e:
                print(f"[ERROR] Validation failed: {e}")
                return None
            
        self.GradeDocuments = GradeDocuments
        self.GradeHallucination = GradeHallucination
        self.AnswerGrader = AnswerGrader
        
        # grader_system_prompt = """
        #     You are a grader assessing relevance of a retrieved document to a user question. \n 
        #     It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
        #     If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        #     Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
        # """
        grader_system_prompt = """
            You are a grader assessing relevance of a retrieved document to a user question. 
            Respond STRICTLY in JSON format with ONE key: 'relevance_score' ('yes' or 'no').
            Example: {"relevance_score": "yes"}
            DO NOT INCLUDE ANY OTHER TEXT.
        """

        hallucination_system_prompt = """
            You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
            Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts.
        """
        answer_system_prompt = """
            You are a grader assessing whether an answer addresses / resolves a question \n 
            Give a binary score 'yes' or 'no'. Yes means that the answer resolves the question.
        """
        improve_system_prompt = """
            You a question re-writer that converts an input question to a better version that is optimized for vectorstore retrieval. \n
            
            Look at the input and try to reason about the underlying semantic intent / meaning.
        """

        grade_prompt = ChatPromptTemplate.from_messages([
            ("system", grader_system_prompt),
            ("human", "Retrieved documents:\n\n{documents}\n\nUser question: {question}")  # 오타 수정 및 변수 정리
        ])

        write_prompt = hub.pull("rlm/rag-prompt")
        hallucination_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", hallucination_system_prompt),
                ("human", "Set of facts : \n\n {documents} \n\n LLM generation : {generation}")
            ]
        )
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", answer_system_prompt),
                ("human", "User question : \n\n {question} \n\n LLM generation : {generation}")
            ]
        )
        improve_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", improve_system_prompt),
                ("human", "Here is the initial question : \n\n {question} \n Formulation an improved question")
            ]
        )

        from langchain_core.output_parsers import JsonOutputParser

        # GradeDocuments용 파서 추가
        grade_documents_parser = JsonOutputParser(pydantic_object=self.GradeDocuments)

        # 체인 재구성 (LLM + 파서 포함)
        self.retrieval_grader = (
            grade_prompt 
            | llm 
            | grade_documents_parser  # JSON 응답을 Pydantic 모델로 변환
        )
        self.writer = grade_prompt | llm # | StrOutputParser()
        self.hallucination_grader = hallucination_prompt | self.GradeHallucination
        self.answer_grader = answer_prompt | self.AnswerGrader
        self.query_improver = improve_prompt | llm # | StrOutputParser()

        self.web_search_tool = TavilySearchResults(k=3)

        self.retrieve = vector_store.as_retriever(
            dynamic_update=True
        )

    
    async def retrieve_node(self, state):
        """
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        print("[Graph Log] RETRIEVE ...")
        question = state["question"]
        session_id = state["session_id"]
        
        try : 
            prev_documents = state["documents"]
            retrieved_documents = await self.retrieve.ainvoke(
                input = question, 
                filter={
                        "session_id" : session_id
                }
            )
            documents = prev_documents + retrieved_documents
        except:
            documents = await self.retrieve.ainvoke(
                input = question, 
                filter={
                        "session_id" : session_id
                }
            )

        state["documents"] = documents
    
        return state
    
    async def write_node(self, state):
        """
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """

        print("[Graph Log] WRITE ...")

        question = state["question"]
        documents = state["documents"]

        # save source of documents
        source = []
        for document in documents:
            source.append(document.metadata["source"])
        state["source"] = list(np.unique(source))

        updated_messages = add_messages(state["messages"], HumanMessage(content=question))
        state["messages"] = updated_messages

        generation = await self.writer.ainvoke({"context" : documents, "question" : question})

        state["generation"] = generation
        updated_messages = add_messages(state["messages"], AIMessage(content=generation))
        state["messages"] = updated_messages

        return state
    
    async def filter_documents_node(self, state):
        """
        Determines whether the retrieved documents are relevant to the question.

        Args : 
            state (dict) : The current graph state

        Returns : 
            state (dict) : Updates documents key with only filterd relevant documents
        """

        print("[Graph Log] FILTER DOCUMENTS ...")
        question = state["question"]
        documents = state["documents"]
        
        filtered_docs = await self.filter_documents(question=question, documents=documents)

        state["documents"] = filtered_docs
        
        return state
    

    async def improve_query_node(self, state):
        """
        Transform the query to produce a better question.

        Args :
            state (dict) : The current graph state
        
        Returns : 
            state (dict) : Updateds question key with a re-phrase question
        """

        print("[Graph Log] TRANSFORM QUERY ...")

        question = state["question"]

        improved_query = await self.query_improver.ainvoke({"question" : question})

        state['question'] = improved_query.content

        return state
    
    async def web_search_node(self, state):
        """
        Web search based on the re-phrased question.

        Args :
            state (dict) : The current graph state

        Returns :
            state (dict) : Updates documents key with appended web results
        """

        print("[Graph Log] WEB SEARCH ...")
        question = state["question"]
        documents = state["documents"]

        if isinstance(question, str):
            query = question
        else:
            query = str(question.content) if hasattr(question, 'content') else str(question)

        docs = await self.web_search_tool.ainvoke({"query" : query, "days" : 30})
        
        web_results = Parallel(n_jobs=4)(delayed(cvt_2_doc)(doc) for doc in docs)

        documents.extend(web_results)

        state["documents"] = documents

        return state
    
    async def decide_write_or_improve_query(self, state):
        """
        Determines whether to generate an answer, or re-generate a question.

        Args : 
            state (dict) : The current graph state
        
        Returns :
            str : Binary decision for next node to call
        """

        print("[Graph Log] DETERMINES 'WRITE' OR 'REWRITE QUESTION' ...")

        documents = state["documents"]

        if len(documents) >= 6:
            print(
                "[Graph Log] DECISION : WRITE"
            )
            return "writer"
        else :
            print(
                "[Graph Log] DECISION : REWRITE QUESTION"
            )
            return "improve_query"
    
    async def decide_to_regenerate_or_rewrite_query_or_end(self, state):
        """
        Determines whether the generation is grounded in the document and answers question.

        Args:
            state (dict) : The current graph state
        
        Returns :
            str : Decision for next node to call
        """

        print("[Graph Log] CHECK HALLUCINATIONS ...")

        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = await self.hallucination_grader.ainvoke(
            {"documents" : documents, "generation" : generation}
        )
        hallucination_grade = score.hallucination_score

        if hallucination_grade == "yes":
            print("[Graph Log] DECISION : ANSWER IS GROUNDED IN DOCUMENTS")

            print("[Graph Log] CHECK ANSWER IS USEFUL OR NOT ...")

            score = await self.answer_grader.ainvoke(
                {"question" : question, "generation" : generation}
            )
            answer_grade = score.answer_score

            if answer_grade == "yes":
                print("[Graph Log] DECISION : GENERATION ADDRESSES QUESTION")

                return "useful"
            else :
                print("[Graph Log] DECISION : GENERATION DOES NOT ADDRESS QUESTION")

                return "not useful"
        else:
            print("[Graph Log] DECISION : GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY")
            
            return "not supported"
    
    async def document_filter(self, question, doc):
        try:
            response = await self.retrieval_grader.ainvoke(
                {"question": question, "documents": doc.page_content}
            )
            # 응답이 딕셔너리인지 확인
            if isinstance(response, dict):
                relevance_grade = response.get("relevance_score", "no")
            else:
                relevance_grade = response.relevance_score  # Pydantic 모델인 경우
        except Exception as e:
            print(f"[ERROR] Validation failed: {e}")
            relevance_grade = "no"  # 실패 시 기본값 처리

        if relevance_grade == "yes":
            print("[Relevance Grader Log] GRADE : DOCUMENT RELEVANT")
            return doc
        else:
            print("[Relevance Grader Log] GRADE : DOCUMENT NOT RELEVANT")
            return None

    async def filter_documents(self, question, documents):
        tasks = [self.document_filter(question=question, doc=doc) for doc in documents]
        filtered_documents = await asyncio.gather(*tasks)

        return [doc for doc in filtered_documents if doc is not None]
    