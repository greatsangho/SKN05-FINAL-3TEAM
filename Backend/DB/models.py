from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.sql import func
from .database import Base

# 유저 로그인 정보
class Member(Base):
    __tablename__ = "member_tbl"
    user_email = Column(String(40), primary_key=True, nullable=False)
    login_time = Column(DateTime, nullable=False, default=func.now())  # DB에서 현재 시간 자동 설정

# SessionID Table
class SessionID(Base):
    __tablename__ = "session_tbl"
    user_email = Column(String(40), ForeignKey('member_tbl.user_email'), nullable=False)
    docs_id = Column(String(100), nullable=False)
    session_id = Column(String(36), unique=True, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_email', 'docs_id', name='pk_user_docs'),  # Composite Primary Key
    )

# QnA Table
class QnA(Base):
    __tablename__ = "qna_tbl"
    qna_id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incremented Primary Key
    user_email = Column(String(40), nullable=False)
    docs_id = Column(String(100), nullable=False)
    session_id = Column(String(36), ForeignKey('session_tbl.session_id'), nullable=False)
    question = Column(String(1000), nullable=False)
    answer = Column(String(1000), nullable=True)
    chat_option = Column(String(20), nullable=False)
    ask_time = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_email', 'docs_id'], 
            ['session_tbl.user_email', 'session_tbl.docs_id'],  # Reference composite PK in SessionID table
        ),
    )

# PDFFile Table
class PDFFile(Base):
    __tablename__ = "pdf_tbl"
    pdf_id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incremented Primary Key
    user_email = Column(String(40), nullable=False)
    docs_id = Column(String(100), nullable=False)
    file_name = Column(String(100), nullable=False)
    file_time = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_email', 'docs_id'], 
            ['session_tbl.user_email', 'session_tbl.docs_id'],  # Reference composite PK in QnA table
        ),
    )
