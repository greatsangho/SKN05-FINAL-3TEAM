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
    redirect_uri=REDIRECT_URI
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
