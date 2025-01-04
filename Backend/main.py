from typing import Annotated
from dotenv import load_dotenv
from starlette.requests import Request

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth, OAuthError

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import uvicorn
import os

app = FastAPI()
load_dotenv()
app.add_middleware(SessionMiddleware, secret_key="sa4givjsadf453576l5l23f0baq345634l63t1f")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': 'http://localhost:8000/auth'
    }
)

@app.get("/")
def hello():
    return {"Hello": "FastAPI",
            "message": "goto /docs to see the documentation"}

@app.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)

from fastapi.responses import RedirectResponse

@app.get("/auth")
async def login(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return {'request': request, 'error': e.error}
    
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    
    # 프론트엔드 URL로 리다이렉트
    frontend_url = "http://localhost:5500/welcome"  # 프론트엔드의 리다이렉트 페이지 URL
    return RedirectResponse(frontend_url)
    

@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')

if __name__ == "__main__":
    uvicorn.run(
        app="app.main:app",
        host="localhost",
        port=8000,
        reload=True
    )
