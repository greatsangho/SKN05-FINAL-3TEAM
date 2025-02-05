########################### Import Modules ###########################
import os
import numpy as np

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# Writer
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langgraph.types import StreamWriter

# define tools
from langchain_community.tools.tavily_search import TavilySearchResults

# define Nodes
from langchain.schema import Document

# load retriever
from langchain_community.vectorstores import FAISS

# messages
from langgraph.graph.message import add_messages

class ParagraphProcess:
    def __init__(self, vector_store : FAISS):
        llm = ChatOpenAI(
            model = "gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )

        ########### Structured Answer Data Model ###########
        class GradeDocuments(BaseModel):
            """
            Binary score for relevance check on retrieved documents.
            """

            relevance_score : str = Field(
                description="Document are relevant to the question, 'yes' or 'no'"
            )

        class GradeHallucination(BaseModel):
            """
            Binary Score for hallunination present in generation answer.
            """

            hallucination_score : str = Field(
                description="Answer is grounded in the facts, 'yes' or 'no'"
            )

        class AnswerGrader(BaseModel):
            """
            Binary Score to assess answer address question.
            """

            answer_score : str = Field(
                description="Answer address the question, 'yes' or 'no'"
            )
        
        grader_structured_llm = llm.with_structured_output(GradeDocuments)
        hallucination_structured_llm = llm.with_structured_output(GradeHallucination)
        answer_structured_llm = llm.with_structured_output(AnswerGrader)

        grader_system_prompt = """
            You are a grader assessing relevance of a retrieved document to a user question. \n 

            It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n

            If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n

            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
        """
        hallucination_system_prompt = """
            You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 

            Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts.
        """
        answer_system_prompt = """
            You are a grader assessing whether an answer addresses / resolves a question \n 
            
            Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question.
        """
        improve_system_prompt = """
            You a question re-writer that converts an input question to a better version that is optimized for vectorstore retrieval. \n
            
            Look at the input and try to reason about the underlying semantic intent / meaning.
        """

        grade_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", grader_system_prompt),
                ("human", "Retreived documents : \n\n {documents} \n\n User question : {question}")
            ]
        )
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

        self.retrieval_grader = grade_prompt | grader_structured_llm
        self.writer = write_prompt | llm | StrOutputParser()
        self.hallucination_grader = hallucination_prompt | hallucination_structured_llm
        self.answer_grader = answer_prompt | answer_structured_llm
        self.query_improver = improve_prompt | llm

        self.web_search_tool = TavilySearchResults(k=3)


        self.retrieve = vector_store.as_retriever()

    
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
        
        try : 
            prev_documents = state["documents"]
            retrieved_documents = await self.retrieve.ainvoke(question)
            documents = prev_documents + retrieved_documents
        except:
            documents = await self.retrieve.ainvoke(question)

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

        filtered_docs = []
        for doc in documents:
            score = await self.retrieval_grader.ainvoke(
                {"question" : question, "documents" : doc.page_content}
            )
            relevance_grade = score.relevance_score

            if relevance_grade == "yes":
                print("[Relevance Grader Log] GRADE : DOCUMENT RELEVANT")
                filtered_docs.append(doc)
            else:
                print("[Relevance Grader Log] GRADE : DOCUMENT NOT RELEVANT")
                continue

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

        docs = await self.web_search_tool.ainvoke({"query" : query})
        web_results = [
            Document(
                page_content=doc["content"],
                metadata={
                    "source" : doc["url"]
                }
            ) for doc in docs]
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