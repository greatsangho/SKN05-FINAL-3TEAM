from pydantic import BaseModel

class QueryRequestModel(BaseModel):
    session_id : str
    question : str
    chat_option : str

class DeleteFileRequestModel(BaseModel):
    session_id : str
    file_name : str