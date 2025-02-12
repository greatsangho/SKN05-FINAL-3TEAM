from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List

# -------------------
# Member Schema
# -------------------
class MemberBase(BaseModel):
    user_email: EmailStr

    class Config:
        orm_mode = True

class MemberCreate(MemberBase):
    pass  # No additional fields for creation

class Member(MemberBase):
    login_time: datetime
    
# -------------------
# SessionID Schema
# -------------------
class SessionIDBase(BaseModel):
    user_email: EmailStr
    docs_id: str

    class Config:
        orm_mode = True

class SessionIDCreate(SessionIDBase):
    pass  # No additional fields for creation

class SessionID(SessionIDBase):
    session_id: str  # Unique session identifier


# -------------------
# QnA Schema
# -------------------
class QnABase(BaseModel):
    user_email: EmailStr
    docs_id: str

    class Config:
        orm_mode = True

class QnACreate(QnABase):
    question: str
    chat_option: str

class QnA(QnABase):
    qna_id: int  # Auto-incremented primary key
    session_id: str  # Foreign key referencing session_tbl.session_id
    question: str
    answer: Optional[str] = None  # Nullable field for the answer
    chat_option: str
    ask_time: datetime  # Automatically set by the database
    source: List[str]  # List of references

# -------------------
# PDFFile Schema
# -------------------
class PDFFileBase(BaseModel):
    user_email: EmailStr
    docs_id: str

    class Config:
        orm_mode = True

# 요청 데이터 모델 정의
class DeletePDFRequest(BaseModel):
    session_id: str
    file_name: str

    class Config:
        orm_mode = True

class PDFFileCreate(PDFFileBase):
    file_name: str  # Required field for creating a PDF file entry

class PDFFile(PDFFileBase):
    pdf_id: int  # Auto-incremented primary key
    file_name: str
    file_time: datetime  # Automatically set by the database

# -------------------
# CSVFile delete
# -------------------
class DeleteCSVRequest(BaseModel):
    user_email: EmailStr  # EmailStr으로 타입 일관화
    docs_id: str
    file_name: str

    class Config:
        orm_mode = True
