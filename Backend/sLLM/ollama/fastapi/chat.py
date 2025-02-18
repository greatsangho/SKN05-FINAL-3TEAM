from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOllama(model="EEVE-Korean-10.8B:latest", temperature=0)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Your mission is to translate given sentences into Korean. Your name is 'FinPilot'."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | llm | StrOutputParser()