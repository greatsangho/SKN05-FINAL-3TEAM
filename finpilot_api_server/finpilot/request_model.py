from pydantic import BaseModel
from fastapi import UploadFile

class InputModel(BaseModel):
    question : str
    session_id : str

class QueryRequestModel(BaseModel):
    input : InputModel

class UploadPDFRequestModel(BaseModel):
    pdf_files : list[UploadFile]
    session_id : str

class DeletePDFRequestModel(BaseModel):
    file_name : str
    session_id : str