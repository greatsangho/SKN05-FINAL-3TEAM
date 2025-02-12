from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(model="EEVE-Korean-10.8B:latest", temperature=0)

prompt = ChatPromptTemplate.from_template("{topic} 에 대하여 자세히 설명해 줘.")

chain = prompt | llm | StrOutputParser()