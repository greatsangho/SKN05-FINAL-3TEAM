# # from typing import Annotated
# # from dotenv import load_dotenv
# # from starlette.requests import Request

# # from fastapi import Depends, FastAPI
# # from fastapi.security import OAuth2PasswordBearer
# # from authlib.integrations.starlette_client import OAuth, OAuthError

# # from fastapi.middleware.cors import CORSMiddleware
# # from starlette.middleware.sessions import SessionMiddleware

# # import uvicorn
# # import os

# # app = FastAPI()
# # load_dotenv()
# # app.add_middleware(SessionMiddleware, secret_key="sa4givjsadf453576l5l23f0baq345634l63t1f")

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # oauth = OAuth()
# # oauth.register(
# #     name='google',
# #     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
# #     client_id=os.getenv('GOOGLE_CLIENT_ID'),
# #     client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
# #     client_kwargs={
# #         'scope': 'email openid profile',
# #         'redirect_url': 'http://localhost:8000/auth'
# #     }
# # )

# # @app.get("/")
# # def hello():
# #     return {"Hello": "FastAPI",
# #             "message": "goto /docs to see the documentation"}

# # @app.get("/login")
# # async def login(request: Request):
# #     url = request.url_for('auth')
# #     return await oauth.google.authorize_redirect(request, url)

# # from fastapi.responses import RedirectResponse

# # @app.get("/auth")
# # async def login(request: Request):
# #     try:
# #         token = await oauth.google.authorize_access_token(request)
# #     except OAuthError as e:
# #         return {'request': request, 'error': e.error}
    
# #     user = token.get('userinfo')
# #     if user:
# #         request.session['user'] = dict(user)
    
# #     # 프론트엔드 URL로 리다이렉트
# #     frontend_url = "http://localhost:5500/welcome"  # 프론트엔드의 리다이렉트 페이지 URL
# #     return RedirectResponse(frontend_url)
    

# # @app.get('/logout')
# # def logout(request: Request):
# #     request.session.pop('user')
# #     request.session.clear()
# #     return RedirectResponse('/')

# # if __name__ == "__main__":
# #     uvicorn.run(
# #         app="app.main:app",
# #         host="localhost",
# #         port=8000,
# #         reload=True
# #     )
# from fastapi import FastAPI, HTTPException, Request
# from authlib.integrations.starlette_client import OAuth
# from starlette.middleware.sessions import SessionMiddleware
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# import os
# import uuid


# # 환경 변수 로드
# load_dotenv()
# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# REDIRECT_URI = os.getenv("REDIRECT_URI")

# app = FastAPI()

# # 세션 미들웨어 추가 (OAuth 인증에 필요)
# app.add_middleware(SessionMiddleware, secret_key="asfawefkkwejd3kfh3f8egfuwlh")

# # CORS 설정 (필요한 도메인만 허용)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["GET", "POST"],
#     allow_headers=["*"],
# )

# # OAuth 클라이언트 초기화
# oauth = OAuth()
# oauth.register(
#     name='google',
#     client_id=GOOGLE_CLIENT_ID,
#     client_secret=GOOGLE_CLIENT_SECRET,
#     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
#     client_kwargs={
#         # 'scope': 'openid email profile https://www.googleapis.com/auth/documents.readonly https://www.googleapis.com/auth/drive.file',
#         'scope': 'openid email profile https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/documents'
#     },
#     # redirect_uri=REDIRECT_URI,
# )
# # request.session['state'] = state

# # @app.get("/")
# # async def hello():
# #     return {"hello": "/docs for more info"}

# # @app.get("/auth/google")
# # async def login_with_google(request: Request):
# #     return await oauth.google.authorize_redirect(request, REDIRECT_URI)

# # @app.get("/auth/google/callback")
# # async def google_callback(request: Request):
# #     try:
# #         token = await oauth.google.authorize_access_token(request)
# #         user_info = token.get('userinfo')
# #         return {"access_token": token, "user_info": user_info}
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

# # import requests

# # @app.get("/list_docs")
# # async def list_docs(token: str):
# #     headers = {"Authorization": f"Bearer {token}"}
    
# #     # Google Drive API 호출 예시 (파일 목록 가져오기)
# #     drive_url = "https://www.googleapis.com/drive/v3/files"
# #     drive_response = requests.get(drive_url, headers=headers)
    
# #     return {
# #         "drive_files": drive_response.json()
# #     }

# @app.get("/")
# async def hello():
#     return {"hello": "/docs for more info"}

# @app.get("/auth/google")
# async def login_with_google(request: Request):
#     # Generate a unique state parameter using uuid
#     state = str(uuid.uuid4())
    
#     # Store the state in the session for validation during callback
#     request.session['state'] = state
    
#     # Redirect user to Google's OAuth2 authorization endpoint with the state parameter
#     return await oauth.google.authorize_redirect(request, REDIRECT_URI, state=state)

# @app.get("/auth/google/callback")
# async def google_callback(request: Request):
#     try:
#         # Retrieve the stored state from the session
#         stored_state = request.session.get('state')
        
#         # Retrieve the returned state from Google's response
#         returned_state = request.query_params.get('state')
        
#         # Validate that the stored and returned states match
#         if stored_state != returned_state:
#             raise HTTPException(status_code=400, detail="State mismatch: Possible CSRF attack.")
        
#         # Exchange authorization code for access token
#         token = await oauth.google.authorize_access_token(request)
        
#         # Retrieve user information from the token
#         user_info = token.get('userinfo')
        
#         return {"access_token": token, "user_info": user_info}
    
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

# @app.get("/list_docs")
# async def list_docs(token: str):
#     headers = {"Authorization": f"Bearer {token}"}
    
#     # Example: Call Google Drive API to fetch file list
#     drive_url = "https://www.googleapis.com/drive/v3/files"
#     drive_response = requests.get(drive_url, headers=headers)
    
#     return {
#         "drive_files": drive_response.json()
#     }

from fastapi import FastAPI, HTTPException, Request
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uuid
import requests

# Load environment variables
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

app = FastAPI()

# Add session middleware (required for OAuth)
app.add_middleware(SessionMiddleware, secret_key="your_consistent_secret_key")

# CORS configuration (adjust as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend domain in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize OAuth client with required scopes
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/documents'
    },
    redirect_uri="https://c2ad-59-15-177-240.ngrok-free.app/auth/google/callback"
)

@app.get("/")
async def hello():
    return {"hello": "/docs for more info"}

@app.get("/auth/google")
async def login_with_google(request: Request):
    # Generate a unique state parameter using uuid
    state = str(uuid.uuid4())
    
    # Store the state in the session for validation during callback
    request.session['state'] = state
    
    # Redirect user to Google's OAuth2 authorization endpoint with the state parameter
    return await oauth.google.authorize_redirect(request, REDIRECT_URI, state=state)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    try:
        # Retrieve the stored state from the session
        stored_state = request.session.get('state')
        
        # Retrieve the returned state from Google's response
        returned_state = request.query_params.get('state')
        
        # Validate that the stored and returned states match
        if stored_state != returned_state:
            raise HTTPException(status_code=400, detail="State mismatch: Possible CSRF attack.")
        
        # Exchange authorization code for access token
        token = await oauth.google.authorize_access_token(request)
        
        # Retrieve user information from the token
        user_info = token.get('userinfo')
        
        return {"access_token": token, "user_info": user_info}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.post("/edit_doc")
async def edit_doc(file_id: str, content: str, token: str):
    """
    Edits a Google Doc by appending content to it.

    Args:
        file_id (str): The ID of the Google Doc.
        content (str): The content to append to the document.
        token (str): The OAuth access token.

    Returns:
        dict: The updated document details.
    """
    url = f"https://docs.googleapis.com/v1/documents/{file_id}:batchUpdate"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    body = {
        "requests": [
            {
                "insertText": {
                    "location": {
                        "index": 1  # Insert at the beginning of the document (index 1)
                    },
                    "text": content,
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())
