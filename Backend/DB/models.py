from .database import Base
from sqlalchemy import create_engine, ForeignKey, DateTime, Text, Boolean, func, Integer, String, VARCHAR, Column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# 질문/답변 모델 정의
class userTBL(Base):
    __tablename__ = "userTBL"
    userEmail = Column(VARCHAR(40), primary_key=True)
    loginTime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)

class fileTBL(Base):
    __tablename__ = "fileTBL"
    fileID = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    userEmail = Column(VARCHAR(40), ForeignKey('userTBL.userEmail'), nullable=False)
    docsID = Column(VARCHAR(100), nullable=False)
    isCSV = Column(Boolean, nullable=False, default=False)
    isPDF = Column(Boolean, nullable=False, default=False)

class qnaTBL(Base):
    __tablename__ = "qnaTBL"
    qnaID = Column(Integer, primary_key=True, index=True)
    fileID = Column(String(36), ForeignKey('fileTBL.fileID'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)  # Optional field
    askTime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)
    isDel = Column(Boolean, nullable=False, default=False)

class csvTBL(Base):
    __tablename__ = "csvTBL"
    fileID = Column(String(36), ForeignKey('fileTBL.fileID'), primary_key=True)
    csvName = Column(VARCHAR(100), nullable=True)  # Optional field
    csvTime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)
    isDel = Column(Boolean, nullable=False, default=False)

class pdfTBL(Base):
    __tablename__ = "pdfTBL"
    fileID = Column(String(36), ForeignKey('fileTBL.fileID'), primary_key=True)
    pdfName = Column(VARCHAR(100), nullable=True)  # Optional field
    pdfTime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)
    isDel = Column(Boolean, nullable=False, default=False)
