import dill
from finpilot.vectorstore import load_faiss_from_redis, create_empty_faiss, save_faiss_to_redis
from finpilot.core import FinPilot
from finpilot.memory import LimitedMemorySaver

def get_session_app(redis_client, session_id):
    if redis_client.exists(f"{session_id}_memory_saver"):
        print(f"[Server Log] LOADING MEMORY FOR SESSION ID : {session_id}")
        memory = dill.loads(redis_client.get(f"{session_id}_memory_saver"))
        print(f"[Server Log] MEMORY LOADED FOR SESSION ID : {session_id}")

        print(f"[Server Log] LOADING VECTORSTORE FOR SESSION ID : {session_id}")
        vectorstore = load_faiss_from_redis(redis_client=redis_client, session_id=session_id)
        print(f"[Server Log] VECTORSTORE LOADED FOR SESSION ID : {session_id}")

        print(f"[Server Log] LOADING APPLICATION FOR SESSION ID : {session_id}")
        pilot = FinPilot(memory=memory, vector_store=vectorstore, session_id=session_id)
        print(f"[Server Log] APPLICATION LOADED FOR SESSION ID : {session_id}")

    else:
        print(f"[Server Log] CREATE MEMORY FOR SESSION ID : {session_id}")
        memory = LimitedMemorySaver(capacity=10)
        print(f"[Server Log] MEMORY CREATED FOR SESSION ID : {session_id}")

        print(f"[Server Log] CREATE VECTORESTORE FOR SESSION ID : {session_id}")
        vectorstore = create_empty_faiss()
        print(f"[Server Log] VECTORESTORE CREATED FOR SESSION ID : {session_id}")

        print(f"[Server Log] CREATE MEMORY FOR SESSION ID : {session_id}")
        pilot = FinPilot(memory=memory, vector_store=vectorstore, session_id=session_id)
        print(f"[Server Log] APPLICATION CREATED FOR SESSION ID : {session_id}")
        
        print(f"[Server Log] SAVING MEMORY TO REDIS FOR SESSION ID : {session_id}")
        redis_client.set(f"{session_id}_memory_saver", dill.dumps(memory))
        redis_client.expire(f"{session_id}_memory_saver", 3600)
        print(f"[Server Log] MEMORY SAVED TO REDIS FOR SESSION ID : {session_id}")

        print(f"[Server Log] SAVING VECTORESTORE TO REDIS FOR SESSION ID : {session_id}")
        save_faiss_to_redis(
            redis_client=redis_client,
            session_id=session_id,
            vector_store=vectorstore
        )
        
    return pilot


def get_session_vectorstore(redis_client, session_id):
    # Redis 에서 session data 로드
    if redis_client.exists(f"{session_id}_faiss_index"):
        print(f"[Server Log] LOADING VECTORSTORE FOR SESSION ID : {session_id}")
        vectorstore = load_faiss_from_redis(redis_client=redis_client, session_id=session_id)
        print(f"[Server Log] VECTORSTORE LOADED FOR SESSION ID : {session_id}")
    else:
        print(f"[Server Log] CREATE MEMORY FOR SESSION ID : {session_id}")
        memory = LimitedMemorySaver(capacity=10)
        print(f"[Server Log] MEMORY CREATED FOR SESSION ID : {session_id}")

        print(f"[Server Log] CREATE VECTORESTORE FOR SESSION ID : {session_id}")
        vectorstore = create_empty_faiss()
        print(f"[Server Log] VECTORESTORE CREATED FOR SESSION ID : {session_id}")
        
        print(f"[Server Log] SAVING MEMORY TO REDIS FOR SESSION ID : {session_id}")
        redis_client.set(f"{session_id}_memory_saver", dill.dumps(memory))
        redis_client.expire(f"{session_id}_memory_saver", 3600)
        print(f"[Server Log] MEMORY SAVED TO REDIS FOR SESSION ID : {session_id}")

        print(f"[Server Log] SAVING VECTORESTORE TO REDIS FOR SESSION ID : {session_id}")
        save_faiss_to_redis(
            redis_client=redis_client,
            session_id=session_id,
            vector_store=vectorstore
        )


    return vectorstore