from fastapi import FastAPI
from Middleware.mid_def import add_middlewares
from DB.database import engine, SessionLocal
from DB.models import Base
from dotenv import load_dotenv
from routers import users, sessions, qnas, pdfs, csvs
import uvicorn

load_dotenv()

Base.metadata.create_all(bind=engine)

# app = FastAPI()
app = FastAPI(
    servers=[{"url": "https://finpilotback.duckdns.org", "description": "Production"}],
    openapi_url="/openapi.json"  # 프록시 환경에서 문서 경로 보정
)

# Add middleware
add_middlewares(app)

# url/docs 로 기능 설명 페이지 안내
@app.get("/")
async def hello():
    return {"hello": "/docs for more info"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# -------------------
# 기능 라우터 처리
# -------------------
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(qnas.router, prefix="/qnas", tags=["QnAs"])
app.include_router(pdfs.router, prefix="/pdfs", tags=["PDFs"])
app.include_router(csvs.router, prefix="/csvs", tags=["CSVs"])

# -------------------
# 파이썬 서버 실행
# -------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)