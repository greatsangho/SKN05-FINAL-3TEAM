# Session Cache
from functools import lru_cache
import pickle

# FinPilot Application
from finpilot.core import FinPilot

import os
from config.secret_keys import OPENAI_API_KEY, TAVILY_API_KEY, USER_AGENT, POLYGON_API_KEY

from fastapi import FastAPI, Request, HTTPException
import uvicorn
from redis import Redis
from request_model import RequestModel

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["USER_AGENT"] = USER_AGENT
os.environ["POLYGON_API_KEY"] = POLYGON_API_KEY



# Redis 연결
redis = Redis(host="localhost", port=6379, decode_responses=True)

@lru_cache(maxsize=100)
def get_app(session_id):
    # Redis 에서 session data 로드
    if redis.exists(session_id):
        app = pickle.loads(redis.get(session_id))
    else:
        # 새로운 세션 생성 및 Redis에 저장
        app = FinPilot()
        redis.set(session_id, pickle.dumps(app))
        redis.expire(session_id, 3600)
    return app







app = FastAPI()

@app.post("/query")
async def finpilot_endpoint(json : RequestModel):
    json_input = json.input
    # Session ID 가져오기
    session_id = json_input.session_id
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required!")
    
    app = get_app(session_id)

    question = json_input.question
    if not question:
        raise HTTPException(status_code=400, detail="Question is required!")
    
    answer = app.invoke(question, session_id)

    return {"session_id" : session_id, "answer" : answer}

@app.get("/sessions")
async def list_sessions():
    # Redis에서 활성 세션 리스트 반환
    keys = redis.keys("*")
    return {"active_sessions" : [key for key in keys]}


if __name__ == "__main__" :
    uvicorn.run("main:app", host="127.0.0.1", reload=True)