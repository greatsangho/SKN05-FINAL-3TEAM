# Construct Vector DB / Create retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

def create_test_retriever():

    urls = [
        'https://www.mk.co.kr/news/stock/11209083', # title : 돌아온 외국인에 코스피 모처럼 ‘활짝’…코스닥 700선 탈환
        'https://www.mk.co.kr/news/stock/11209254', # title : 힘 못받는 증시에 밸류업 ETF 두 달째 마이너스 수익률
        'https://www.mk.co.kr/news/stock/11209229', # title : 서학개미 한 달간 1조원 샀는데···테슬라 400달러 붕괴
    ]

    docs = [WebBaseLoader(url).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=50
    )
    doc_splits = text_splitter.split_documents(docs_list)

    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        persist_directory='./rag-chroma',
        collection_name = 'rag-chroma',
        embedding=OpenAIEmbeddings(),
    )

    retrieve = vectorstore.as_retriever()

    return retrieve

def load_test_retriever(dir_path='./rag-chroma'):

    vectorstore = Chroma(
        persist_directory=dir_path,
        collection_name='rag-chroma',
        embedding_function=OpenAIEmbeddings()
    )

    retrieve = vectorstore.as_retriever()

    return retrieve