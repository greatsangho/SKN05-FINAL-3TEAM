from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# -------------------
# Member Schema
# -------------------
class MemberBase(BaseModel):
    user_email: EmailStr

class MemberCreate(MemberBase):
    pass  # No additional fields for creation

class Member(MemberBase):
    login_time: datetime

    class Config:
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models


# -------------------
# SessionID Schema
# -------------------
class SessionIDBase(BaseModel):
    user_email: EmailStr
    docs_id: str

class SessionIDCreate(SessionIDBase):
    pass  # No additional fields for creation

class SessionID(SessionIDBase):
    session_id: str  # Unique session identifier

    class Config:
        orm_mode = True


# -------------------
# QnA Schema
# -------------------
class QnABase(BaseModel):
    user_email: EmailStr
    docs_id: str

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

    class Config:
        orm_mode = True


# -------------------
# PDFFile Schema
# -------------------
class PDFFileBase(BaseModel):
    user_email: EmailStr
    docs_id: str

class DeletePDFRequest(PDFFileBase):
    file_name: str

class PDFFileCreate(PDFFileBase):
    file_name: str  # Required field for creating a PDF file entry

class PDFFile(PDFFileBase):
    pdf_id: int  # Auto-incremented primary key
    file_name: str
    file_time: datetime  # Automatically set by the database

    class Config:
        orm_mode = True

# -------------------
# CSVFile delete
# -------------------
class DeleteCSVRequest(BaseModel):
    user_email: str
    docs_id: str
    file_name: str
