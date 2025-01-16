# Construct Vector DB / Create retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore

import os

import faiss
import dill
import io
import numpy as np
    


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

    vectorstore = FAISS.from_documents(
        documents=doc_splits,
        embedding=OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    )
    vectorstore.save_local("faiss_storage")

    retrieve = vectorstore.as_retriever()

    return retrieve

def load_test_retriever(dir_path='./faiss_storage'):
    vectorstore = FAISS.load_local(
        dir_path,
        embeddings=OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        allow_dangerous_deserialization=True
    )

    retrieve = vectorstore.as_retriever()

    return retrieve


def create_empty_faiss():
    docstore = InMemoryDocstore({})
    index_to_docstore_id = {}

    vector_store = FAISS(
        embedding_function = OpenAIEmbeddings(
            api_key=os.environ['OPENAI_API_KEY']
        ),
        index=faiss.IndexFlatL2(1536),
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )
    return vector_store 


def load_faiss_from_redis(redis_client, session_id):
    # Restore FAISS index
    faiss_binary = redis_client.get(f"{session_id}_faiss_index")
    if not faiss_binary:
        raise ValueError(f"No FAISS index found for session '{session_id}'")
    # faiss_buffer = io.BytesIO(faiss_binary)
    # faiss_buffer.seek(0)
    # faiss_index = faiss.read_index(faiss_buffer)
    faiss_array = np.frombuffer(faiss_binary, dtype=np.uint8)
    faiss_index = faiss.deserialize_index(faiss_array)

    # Restore FAISS Meta data
    metadata_binary = redis_client.get(f"{session_id}_faiss_metadata")
    if not metadata_binary:
        raise ValueError(f"No metadata found for session '{session_id}'")
    metadata = dill.loads(metadata_binary)
    texts = metadata['texts']
    index_to_id = metadata['index_to_id']

    # Restore FAISS vectorStore
    vectorstore = FAISS(
        embedding_function=OpenAIEmbeddings(
            api_key=os.environ['OPENAI_API_KEY']
        ),
        index=faiss_index,
        docstore=InMemoryDocstore(texts),
        index_to_docstore_id=index_to_id
    )
    # vectorstore.docstore._dict = texts
    # vectorstore.index_to_docstore_id = index_to_id

    return vectorstore

def save_faiss_to_redis(redis_client, session_id, vector_store : FAISS):
    # save faiss index
    # faiss_buffer = io.BytesIO()
    # faiss.write_index(vector_store.index, faiss_buffer)
    faiss_buffer = faiss.serialize_index(vector_store.index)
    # redis_client.set(f"{session_id}_faiss_index", faiss_buffer.getvalue())
    redis_client.set(f"{session_id}_faiss_index", faiss_buffer.tobytes())
    redis_client.expire(f"{session_id}_faiss_index", 3600)

    # save metadata
    metadata = dill.dumps({
        "texts" : vector_store.docstore._dict,
        "index_to_id" : vector_store.index_to_docstore_id
    })
    redis_client.set(f"{session_id}_faiss_metadata", metadata)
    redis_client.expire(f"{session_id}_faiss_metadata", 3600)

    print(f"FAISS VectorStore saved to Redis for session '{session_id}'.")


def add_data_to_vectorstore_and_update_redis(redis_client, session_id, vector_store : FAISS, new_data=[]):
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
    new_texts = [doc.page_content for doc in doc_splits]

    vector_store.add_texts(new_texts)
    save_faiss_to_redis(
        redis_client=redis_client,
        session_id=session_id,
        vector_store=vector_store
    )

    print(f"VectorStore updated and saved to Redis for Session '{session_id}'.")