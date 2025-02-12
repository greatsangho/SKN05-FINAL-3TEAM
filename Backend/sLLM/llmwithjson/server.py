from fastapi import FastAPI
from langchain_community.chat_models import ChatOllama
from langserve import add_routes

# Ollama 모델 초기화
llm = ChatOllama(model="EEVE-Korean-10.8B:latest", base_url="http://localhost:11434")

# FastAPI 앱 생성
app = FastAPI(title="LangServe with Ollama", version="1.0", description="LLM API Server using LangServe and Ollama")

# LangServe 경로 추가
add_routes(app, llm, path="/ollama")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
