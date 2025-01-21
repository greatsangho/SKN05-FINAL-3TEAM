import dill
from finpilot.vectorstore import load_faiss_from_redis, create_empty_faiss, save_faiss_to_redis
from finpilot.core import FinPilot
from finpilot.memory import LimitedMemorySaver

def get_session_app(redis_client, session_id):
    # Redis 에서 session data 로드
    if redis_client.exists(f"{session_id}_memory_saver"):
        memory = dill.loads(redis_client.get(f"{session_id}_memory_saver"))
        vectorstore = load_faiss_from_redis(redis_client=redis_client, session_id=session_id)
        pilot = FinPilot(memory=memory, vector_store=vectorstore, session_id=session_id)
        print(f"[Server Log] Application Loaded for session id : {session_id}")
    else:
        # 새로운 세션 생성 및 Redis에 저장
        memory = LimitedMemorySaver(capacity=10)
        vectorstore = create_empty_faiss()
        pilot = FinPilot(memory=memory, vector_store=vectorstore, session_id=session_id)
        
        redis_client.set(f"{session_id}_memory_saver", dill.dumps(memory))
        redis_client.expire(f"{session_id}_memory_saver", 3600)
        save_faiss_to_redis(
            redis_client=redis_client,
            session_id=session_id,
            vector_store=vectorstore
        )
        
    return pilot


def get_session_vectorstore(redis_client, session_id):
    # Redis 에서 session data 로드
    if redis_client.exists(f"{session_id}_faiss_index"):
        vectorstore = load_faiss_from_redis(redis_client=redis_client, session_id=session_id)
        print(f"[Server Log] VectorStore Loaded for session id : {session_id}")
    else:
        # 새로운 세션 생성 및 Redis에 저장
        memory = LimitedMemorySaver(capacity=10)
        vectorstore = create_empty_faiss()
        
        redis_client.set(f"{session_id}_memory_saver", dill.dumps(memory))
        redis_client.expire(f"{session_id}_memory_saver", 3600)
        save_faiss_to_redis(
            redis_client=redis_client,
            session_id=session_id,
            vector_store=vectorstore
        )


    return vectorstore