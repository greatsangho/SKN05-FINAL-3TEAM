from pydantic import BaseModel

class InputModel(BaseModel):
    question : str
    session_id : str

class RequestModel(BaseModel):
    input : InputModel