from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from Middleware.mid_class import TimingMiddleware, RateLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

def add_middlewares(app):
    app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
