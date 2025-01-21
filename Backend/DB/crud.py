from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from .models import Member, SessionID, QnA, PDFFile
from . import schemas
import hashlib
import uuid
import os

# -------------------
# Member CRUD Functions
# -------------------
def create_user(db: Session, user_email: str):
    new_user = Member(user_email=user_email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to get the latest state from the database
    return new_user

def update_user_login_time(db: Session, user_email: str):
    db_user = db.query(Member).filter(Member.user_email == user_email).first()
    if db_user:
        db_user.login_time = func.now()  # Update login time to current time
        db.commit()
        db.refresh(db_user)
        return db_user
    raise ValueError(f"User with email {user_email} does not exist.")

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Member).offset(skip).limit(limit).all()

def get_user_by_email(db: Session, user_email: str):
    return db.query(Member).filter(Member.user_email == user_email).first()

def delete_user(db: Session, user_email: str):
    db_user = db.query(Member).filter(Member.user_email == user_email).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# -------------------
# SessionID CRUD Functions
# -------------------
def create_session(db: Session, user_email: str, docs_id: str):
    # Check if the session already exists
    existing_session = db.query(SessionID).filter(
        SessionID.user_email == user_email,
        SessionID.docs_id == docs_id
    ).first()
    
    if existing_session:
        # If the session already exists, return it without creating a new one
        return existing_session

    # Validate that the user exists
    if not db.query(Member).filter(Member.user_email == user_email).first():
        raise ValueError(f"User with email {user_email} does not exist.")

    # Generate session_id using UUID namespace
    namespace = os.getenv("NAMESPACE_UUID")
    if not namespace:
        raise ValueError("NAMESPACE_UUID environment variable is not set.")
    
    namespace_uuid = uuid.UUID(namespace)
    hashed_name = hashlib.sha256(f"{user_email}-{docs_id}".encode()).hexdigest()
    session_id = str(uuid.uuid5(namespace_uuid, hashed_name))

    # Create a new session
    new_session = SessionID(
        user_email=user_email,
        docs_id=docs_id,
        session_id=session_id,
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def get_sessions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(SessionID).offset(skip).limit(limit).all()

def get_session_by_id(db: Session, session_id: str):
    return db.query(SessionID).filter(SessionID.session_id == session_id).first()

def delete_session(db: Session, session_id: str):
    db_session = db.query(SessionID).filter(SessionID.session_id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False

# -------------------
# QnA CRUD Functions
# -------------------
def create_qna(db: Session, user_email: str, docs_id: str, question: str, session_id: str, chat_option: str):
    """
    QnA 레코드 생성 함수.
    """
    # 세션 유효성 검증 (이미 session_id를 호출부에서 전달받음)
    session = db.query(SessionID).filter(
        SessionID.user_email == user_email,
        SessionID.docs_id == docs_id,
        SessionID.session_id == session_id
    ).first()

    if not session:
        raise ValueError(f"Session with user_email {user_email} and docs_id {docs_id} does not exist.")

    # 새로운 QnA 레코드 생성
    new_qna = QnA(
        user_email=user_email,
        docs_id=docs_id,
        question=question,
        ask_time=func.now(),
        chat_option=chat_option,
        session_id=session.session_id,
    )
    
    db.add(new_qna)
    db.commit()
    db.refresh(new_qna)
    return new_qna


def get_qnas(db: Session, skip: int = 0, limit: int = 10):
    """
    QnA 목록 조회 함수.
    """
    return db.query(QnA).offset(skip).limit(limit).all()


def delete_qna(db: Session, qna_id: int):
    """
    QnA 삭제 함수.
    """
    db_qna = db.query(QnA).filter(QnA.qna_id == qna_id).first()
    
    if db_qna:
        db.delete(db_qna)
        db.commit()
        return True
    
    return False

def get_qnas(db: Session, skip: int = 0, limit: int = 10):
    return db.query(QnA).offset(skip).limit(limit).all()

def get_qna_by_id(db: Session, qna_id: int):
    return db.query(QnA).filter(QnA.qna_id == qna_id).first()

def delete_qna(db: Session, qna_id: int):
    db_qna = db.query(QnA).filter(QnA.qna_id == qna_id).first()
    if db_qna:
        db.delete(db_qna)
        db.commit()
        return True
    return False

# -------------------
# PDFFile CRUD Functions
# -------------------
def create_pdf_file(db: Session, user_email: str, docs_id: str, file_name: str):
    # Validate that the SessionID entry exists
    session_entry = db.query(SessionID).filter(
        SessionID.user_email == user_email,
        SessionID.docs_id == docs_id
    ).first()

    if not session_entry:
        raise ValueError(f"QnA entry with user_email {user_email} and docs_id {docs_id} does not exist.")

    # Create a new PDF file entry
    new_pdf_file = PDFFile(
        user_email=user_email,
        docs_id=docs_id,
        file_name=file_name,
        file_time=func.now(),
    )
    
    db.add(new_pdf_file)
    db.commit()
    db.refresh(new_pdf_file)
    return new_pdf_file

def update_pdf_file_name(db: Session, pdf_id: int, new_file_name: str):
    pdf_file = (
        db.query(PDFFile)
        .filter(PDFFile.pdf_id == pdf_id)
        .first()
    )
    
    if pdf_file:  # Ensure this line is indented correctly
        pdf_file.file_name = new_file_name  # Update the file name
        db.commit()
        db.refresh(pdf_file)
        return pdf_file
    
    raise ValueError(f"PDF file with id {pdf_id} does not exist.")


def get_pdf_file(db: Session, user_email: str, docs_id: str, file_name: str):
    """
    Retrieve a PDF file entry based on user_email, docs_id, and file_name.
    """
    return (
        db.query(PDFFile)
        .filter(
            PDFFile.user_email == user_email,
            PDFFile.docs_id == docs_id,
            PDFFile.file_name == file_name
        )
        .first()
    )

def delete_pdf_file(db: Session, pdf_id: int):
    pdf_file = (
        db.query(PDFFile)
        .filter(PDFFile.pdf_id == pdf_id)
        .first()
    )
    
    if pdf_file:  # Ensure this line is indented correctly
        db.delete(pdf_file)
        db.commit()
        return True
    
    return False