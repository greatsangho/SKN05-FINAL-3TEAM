from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
import os
import uuid
import requests

# Load environment variables
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# 웹 상에서 구글 로그인 기능 --> 크롬 익스텐션에서 불필요(미사용)
# 웹 상에서 구글 로그인 시 사용 가능
# Initialize OAuth client with required scopes
# Scope 부분에서 구글 권한 요청
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

# 구글 로그인 구현
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