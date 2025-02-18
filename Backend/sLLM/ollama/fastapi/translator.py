from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(model="EEVE-Korean-10.8B:latest", temperature=0)

prompt = ChatPromptTemplate.from_template("Translate the following sentences into Korean:\n{input}")

chain = prompt | llm | StrOutputParser()