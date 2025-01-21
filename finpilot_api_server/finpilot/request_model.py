from pydantic import BaseModel
from fastapi import UploadFile

class QueryRequestModel(BaseModel):
    session_id : str
    question : str
    chat_option : str

class UploadPDFRequestModel(BaseModel):
    session_id : str
    file : UploadFile

class DeletePDFRequestModel(BaseModel):
    session_id : str
    file_name : str

class UploadCSVRequestModel(BaseModel):
    session_id : str
    file : UploadFile