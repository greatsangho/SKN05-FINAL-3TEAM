from pydantic import BaseModel
from fastapi import UploadFile, File

class InputModel(BaseModel):
    question : str
    session_id : str

class QueryRequestModel(BaseModel):
    input : InputModel

class UploadPDFRequestModel(BaseModel):
    pdf_files : list[UploadFile] = File(...)
    session_id : str