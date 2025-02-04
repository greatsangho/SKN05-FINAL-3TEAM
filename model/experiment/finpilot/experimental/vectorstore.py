# Construct Vector DB / Create retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document

import os

import faiss
import numpy as np


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


def add_data_to_vectorstore(vector_store : FAISS, data : list[Document]):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=50
    )
    doc_splits = text_splitter.split_documents(data)

    vector_store.add_documents(doc_splits)

    return vector_store

def delete_data_from_vectorstore(vector_store : FAISS, file_name):

    # find document id to remove with file name
    doc_ids_to_delete = [
        idx for idx, doc in vector_store.docstore._dict.items() if doc.metadata.get('filename') == file_name
    ]

    if not doc_ids_to_delete:
        print("[Server Log] NO SUCH FILES")
        return None

    faiss_ids_to_delete = [
        faiss_id for faiss_id, doc_id in vector_store.index_to_docstore_id.items() if doc_id in doc_ids_to_delete
    ]

    if not faiss_ids_to_delete:
        print("[Server Log] NO VECTORS FOUND TO DELETE!")
        return None
    
    vector_store.index.remove_ids(np.array(faiss_ids_to_delete, dtype=np.int64))
    
    for doc_id in sorted(doc_ids_to_delete, reverse=True):
        del vector_store.docstore._dict[doc_id]
    
    for faiss_id in sorted(faiss_ids_to_delete, reverse=True):
        del vector_store.index_to_docstore_id[faiss_id]
    
    return vector_store