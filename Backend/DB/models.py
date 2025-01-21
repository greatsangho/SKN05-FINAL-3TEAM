from sqlalchemy import Column, String, DateTime, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.sql import func
from .database import Base

# 유저 로그인 정보
class Member(Base):
    __tablename__ = "member_tbl"
    user_email = Column(String(40), primary_key=True, nullable=False)
    login_time = Column(DateTime, nullable=False, default=func.now())  # DB에서 현재 시간 자동 설정

# QnA 테이블
class QnA(Base):
    __tablename__ = "qna_tbl"
    session_id = Column(String(36), nullable=False)
    user_email = Column(String(40), ForeignKey('member_tbl.user_email'), nullable=False)
    docs_id = Column(String(100), nullable=False)
    question = Column(String(1000), nullable=False)
    answer = Column(String(1000), nullable=True)
    ask_time = Column(DateTime, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_email', 'docs_id', name='pk_user_docs'),  # Composite Primary Key
    )

# PDFFile 테이블
class PDFFile(Base):
    __tablename__ = "pdf_tbl"
    user_email = Column(String(40), nullable=False)
    docs_id = Column(String(100), nullable=False)
    file_name = Column(String(100), nullable=False)
    file_time = Column(DateTime, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_email', 'docs_id'], 
            ['qna_tbl.user_email', 'qna_tbl.docs_id'],  # Reference composite PK in QnA table
        ),
        PrimaryKeyConstraint('user_email', 'docs_id'),  # Composite PK for pdf_tbl
    )