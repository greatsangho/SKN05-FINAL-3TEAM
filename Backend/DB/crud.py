from sqlalchemy.orm import Session
from .models import Member, QnA, PDFFile
from sqlalchemy.sql import func
from . import schemas
import uuid
import hashlib

# Member CRUD Functions
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

# QnA CRUD Functions
def create_qna(db: Session, user_email: str, docs_id: str, question: str):
    # Generate session_id based on user_email and docs_id using UUID v5

    namespace = uuid.UUID("12345678-1234-5678-1234-567812345678")  # Replace with your own namespace UUID
    hashed_name = hashlib.sha256(f"{user_email}-{docs_id}".encode()).hexdigest()
    session_id = str(uuid.uuid5(namespace, hashed_name))

    new_qna = QnA(
        session_id=session_id,
        user_email=user_email,
        docs_id=docs_id,
        question=question,
        ask_time=func.now()
    )
    
    db.add(new_qna)
    db.commit()
    db.refresh(new_qna)
    return new_qna

def get_qnas(db: Session, skip: int = 0, limit: int = 10):
    return db.query(QnA).offset(skip).limit(limit).all()

def get_qna_by_session_id(db: Session, session_id: str):
    return db.query(QnA).filter(QnA.session_id == session_id).first()

def delete_qna(db: Session, session_id: str):
    db_qna = db.query(QnA).filter(QnA.session_id == session_id).first()
    if db_qna:
        db.delete(db_qna)
        db.commit()
        return True
    return False

# PDF CRUD Functions
def create_pdf_file(db: Session, user_email: str, docs_id: str, file_name: str):
    new_pdf_file = PDFFile(
        user_email=user_email,
        docs_id=docs_id,
        file_name=file_name,
        file_time=func.now()
    )
    db.add(new_pdf_file)
    db.commit()
    db.refresh(new_pdf_file)
    return new_pdf_file

def update_pdf_file_name(db: Session, user_email: str, docs_id: str, new_file_name: str):
    db_pdf_file = (
        db.query(PDFFile)
        .filter(PDFFile.user_email == user_email, PDFFile.docs_id == docs_id)
        .first()
    )
    if db_pdf_file:
        db_pdf_file.file_name = new_file_name  # Update the file name
        db.commit()
        db.refresh(db_pdf_file)
        return db_pdf_file
    raise ValueError(f"PDF file with user_email {user_email} and docs_id {docs_id} does not exist.")

def get_pdfs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(PDFFile).offset(skip).limit(limit).all()

def delete_pdf_file(db: Session, user_email: str, docs_id: str):
    db_pdf_file = (
        db.query(PDFFile)
        .filter(PDFFile.user_email == user_email, PDFFile.docs_id == docs_id)
        .first()
    )
    if db_pdf_file:
        db.delete(db_pdf_file)
        db.commit()
        return True
    return False