from finpilot.utils import parse_pdf
from finpilot.vectorstore import add_data_to_vectorstore, delete_data_from_vectorstore

async def upload_pdfs(
    session_id, file, vector_store
):
    # Parsing PDF File And Transform as Document object
    documents = []
    document = await parse_pdf(file=file, session_id=session_id)
    documents.append(document)

    # Add data to Session VectorStore & Update Redis Server Data
    vector_store = await add_data_to_vectorstore(
        vector_store=vector_store,
        data=documents
    )

    return vector_store


async def delete_pdfs(
    file_name, session_id, vector_store
):
    # delete data from Session VectorStore & Update Redis Server Data
    vector_store = await delete_data_from_vectorstore(
        session_id=session_id,
        vector_store=vector_store,
        file_name=file_name
    )

    return vector_store