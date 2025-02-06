from finpilot.utils import parse_pdf
from finpilot.session import get_session_vectorstore
from finpilot.vectorstore import add_data_to_vectorstore_and_update_redis, delete_data_from_vectorstore_and_update_redis

async def upload_pdfs(
    session_id, file, redis
):
    # Parsing PDF File And Transform as Document object
    documents = []
    document = parse_pdf(file)
    documents.append(document)

    # Get VectorStore accoring to Session ID
    vectorstore = get_session_vectorstore(
        redis_client=redis,
        session_id=session_id
    )

    # Add data to Session VectorStore & Update Redis Server Data
    add_data_to_vectorstore_and_update_redis(
        redis_client=redis,
        session_id=session_id,
        vector_store=vectorstore,
        data=documents
    )


async def delete_pdfs(
    file_name, session_id, redis
):
    # Get VectorStore accoring to Session ID
    vectorstore = get_session_vectorstore(
        redis_client=redis,
        session_id=session_id
    )
    
    # delete data from Session VectorStore & Update Redis Server Data
    delete_data_from_vectorstore_and_update_redis(
        redis_client=redis,
        session_id=session_id,
        vector_store=vectorstore,
        file_name=file_name
    )