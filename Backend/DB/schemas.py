from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# -------------------
# Pydantic 모델 정의
# -------------------

# -------------------
# 유저 정보 정의
# -------------------
class UserBase(BaseModel):
    userEmail: str
    loginTime: Optional[datetime] = None
# Create 요청 스키마
class UserCreate(UserBase):
    pass  # 모든 필드를 그대로 사용

# Update 요청 스키마 (부분 업데이트 허용)
class UserUpdate(BaseModel):
    loginTime: Optional[datetime]

# Response 스키마
class UserResponse(UserBase):
    class Config:
        orm_mode = True  # SQLAlchemy 모델과 호환되도록 설정

# -------------------
# 구글 독스 파일 정의
# -------------------
class FileBase(BaseModel):
    userEmail: str
    docsID: str
    isCSV: bool
    isPDF: bool

# Create 요청 스키마
class FileCreate(FileBase):
    pass  # 모든 필드를 그대로 사용

# Update 요청 스키마 (부분 업데이트 허용)
class FileUpdate(BaseModel):
    docsID: Optional[str]
    isCSV: Optional[bool]
    isPDF: Optional[bool]

# Response 스키마
class FileResponse(FileBase):
    fileID: int  # Primary Key 포함

    class Config:
        orm_mode = True  # SQLAlchemy 모델과 호환되도록 설정

# -------------------
# 질문 정의
# -------------------
class QnaBase(BaseModel):
    question: str
    answer: Optional[str] = None
    fileID: Optional[int] = None  # fileID는 외래 키로 선택적 필드
    isDel: bool = False

# Create 요청 스키마
class QnaCreate(QnaBase):
    pass  # 모든 필드를 그대로 사용

# Update 요청 스키마 (부분 업데이트 허용)
class QnaUpdate(BaseModel):
    question: Optional[str]
    answer: Optional[str]
    fileID: Optional[int]
    isDel: Optional[bool]
# Response 스키마
class QnaResponse(QnaBase):
    qnaID: int  # Primary Key 포함

    class Config:
        orm_mode = True  # SQLAlchemy 모델과 호환되도록 설정

# -------------------
# csv 파일 정의
# -------------------
class CsvBase(BaseModel):
    fileID: int
    csvName: Optional[str] = None
    csvTime: Optional[datetime] = None
    isDel: bool

# Create 요청 스키마
class CsvCreate(CsvBase):
    pass  # 모든 필드를 그대로 사용

# Update 요청 스키마 (부분 업데이트 허용)
class CsvUpdate(BaseModel):
    csvName: Optional[str]
    isDel: Optional[bool]

# Response 스키마
class CsvResponse(CsvBase):
    class Config:
        orm_mode = True  # SQLAlchemy 모델과 호환되도록 설정

# -------------------
# pdf 파일 정의
# -------------------   
class PdfBase(BaseModel):
    fileID: int
    pdfName: Optional[str] = None
    pdfTime: Optional[datetime] = None
    isDel: bool

# Create 요청 스키마
class PdfCreate(PdfBase):
    pass  # 모든 필드를 그대로 사용

# Update 요청 스키마 (부분 업데이트 허용)
class PdfUpdate(BaseModel):
    pdfName: Optional[str]
    isDel: Optional[bool]

# Response 스키마
class PdfResponse(PdfBase):
    class Config:
        orm_mode = True  # SQLAlchemy 모델과 호환되도록 설정
        
