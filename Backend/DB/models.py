# class User(Base):
#     __tablename__ = 'Users'
    
#     u_id: Mapped[int] = mapped_column(String(36), primary_key=True, autoincrement=True)
#     u_name: Mapped[str] = mapped_column(String(32), nullable=False)
#     u_email: Mapped[str] = mapped_column(String(64), nullable=False)
#     u_password: Mapped[str] = mapped_column(String(64), nullable=True)
#     u_created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
#     u_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

from .database import Base
from sqlalchemy import create_engine, Column, Integer, String, Text, VARCHAR, Boolean, ForeignKey, DateTime, func
from datetime import datetime

# 질문/답변 모델 정의
class userTBL(Base):
    __tablename__ = "userTBL"
    userEmail = Column(VARCHAR(40), primary_key=True, index=True)
    userID = Column(VARCHAR(40), nullable=False)
    userLName = Column(VARCHAR(20), nullable=True)
    userFName = Column(VARCHAR(20), nullable=False)
    userImg = Column(VARCHAR(100), nullable=True)
    userToken = Column(VARCHAR(50), nullable=True)

class fileTBL(Base):
    __tablename__="fileTBL"
    fileID = Column(Integer, primary_key=True)
    userEmail = Column(VARCHAR(40), ForeignKey('userTBL.userEmail'), nullable=False)
    docsID = Column(VARCHAR(100), nullable=False)
    isCSV = Column(Boolean, nullable=False)
    isPDF = Column(Boolean, nullable=False)

class qnaTBL(Base):
    __tablename__ = "qnaTBL"
    qnaID = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    askTime = Column(DateTime, nullable=False)
    fileID = Column(Integer, ForeignKey('fileTBL.fileID'))

class csvTBL(Base):
    __tablename__ = "csvTBL"
    fileID = Column(Integer, ForeignKey('fileTBL.fileID'), primary_key=True)
    csvName = Column(VARCHAR(100), nullable=True)
    csvTime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)
    isDel = Column(Boolean, nullable=False)

class pdfTBL(Base):
    __tablename__ = "pdfTBL"
    fileID = Column(Integer, ForeignKey('fileTBL.fileID'), primary_key=True)
    pdfName = Column(VARCHAR(100), nullable=True)
    pdfTime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)
    isDel = Column(Boolean, nullable=False)

class loginHistoryTBL(Base):
    __tablename__ = "loginHistoryTBL"
    loginID = Column(Integer, primary_key=True, index=True)
    userEmail = Column(VARCHAR(40), ForeignKey('userTBL.userEmail'), nullable=False)
    loginTime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow)
