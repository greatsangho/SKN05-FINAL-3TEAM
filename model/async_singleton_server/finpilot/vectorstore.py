# Construct Vector DB / Create retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document


async def add_data_to_vectorstore(vector_store : Chroma, data : list[Document]):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=50
    )
    doc_splits = text_splitter.split_documents(data)

    await vector_store.aadd_documents(doc_splits)

    return vector_store

async def delete_data_from_vectorstore(vector_store : Chroma, file_name, session_id):
    source_match = set(vector_store._collection.get(
        where={"source" : file_name}
    )["ids"])

    file_match = set(vector_store._collection.get(
        where={"session_id" : session_id}
    )["ids"])

    doc_ids_to_delete = list(source_match.intersection(file_match))

    if not doc_ids_to_delete:
        print("[Server Log] NO SUCH FILES")
        return None
    
    # vector_store._collection.delete(ids=doc_ids_to_delete)
    await vector_store.adelete(ids=doc_ids_to_delete)

    return vector_store