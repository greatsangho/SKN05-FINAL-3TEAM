from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Member Schema
class MemberBase(BaseModel):
    user_email: EmailStr

class MemberCreate(MemberBase):
    pass  # No additional fields; you can omit this schema if unnecessary

class Member(MemberBase):
    login_time: datetime

    class Config:
        orm_mode = True


class QnABase(BaseModel):
    user_email: EmailStr
    docs_id: str

class QnACreate(QnABase):
    question: str

class QnA(QnABase):
    session_id: str
    question: str
    answer: Optional[str] = None  # Included in response, not input
    ask_time: datetime

    class Config:
        orm_mode = True

# PDF Schema
class PDFFileBase(BaseModel):
    user_email: EmailStr
    docs_id: str

class PDFFileCreate(PDFFileBase):
    file_name: str
    file_time: datetime = datetime.now()  # Default to current timestamp

class PDFFile(PDFFileBase):
    file_name: str
    file_time: datetime

    class Config:
        orm_mode = True
