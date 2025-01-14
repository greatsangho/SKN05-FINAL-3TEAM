from sqlalchemy.orm import Session
from .models import userTBL, fileTBL, qnaTBL, csvTBL, pdfTBL
from .schemas import UserCreate, UserUpdate
from .schemas import FileCreate, FileUpdate, QnaCreate, QnaUpdate
from .schemas import CsvCreate, CsvUpdate, PdfCreate, PdfUpdate
import uuid

def generate_uuid(user_email: str, docs_id: str) -> str:
    # Combine userEmail and docsID into a single string
    combined_string = f"{user_email}:{docs_id}"
    # Generate a UUID based on the combined string
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, combined_string))

# -------------------
# 유저 정보 CRUD
# -------------------
# Create (사용자 생성)
def create_user(db: Session, user: UserCreate):
    db_user = userTBL(**user.dict())  # Pydantic 데이터를 SQLAlchemy 모델로 변환
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # 새로 생성된 객체 반환
    return db_user

# Read (모든 사용자 조회)
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(userTBL).offset(skip).limit(limit).all()

# Read (특정 사용자 조회)
def get_user_by_email(db: Session, user_email: str):
    return db.query(userTBL).filter(userTBL.userEmail == user_email).first()

# Update (사용자 로그인 기록 업데이트)
def update_user(db: Session, user_email: str, updates: UserUpdate):
    db_user = db.query(userTBL).filter(userTBL.userEmail == user_email).first()
    if not db_user:
        return None  # 사용자 없음
    
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_user, key, value)  # 업데이트된 값만 적용
    
    db.commit()
    db.refresh(db_user)
    return db_user

# Delete (사용자 삭제)
def delete_user(db: Session, user_email: str):
    db_user = db.query(userTBL).filter(userTBL.userEmail == user_email).first()
    if not db_user:
        return None  # 사용자 없음
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

# -------------------
# 구글 독스 파일 정보 CRUD
# -------------------
# Create (파일 생성)
def create_file(db: Session, file: FileCreate):
    # Generate fileID using userEmail and docsID
    file_id = generate_uuid(file.userEmail, file.docsID)

    # Check if the file already exists (optional)
    existing_file = db.query(fileTBL).filter(fileTBL.fileID == file_id).first()
    if existing_file:
        raise HTTPException(status_code=400, detail="File with the same userEmail and docsID already exists.")

    # Create a new file record
    db_file = fileTBL(
        fileID=file_id,
        userEmail=file.userEmail,
        docsID=file.docsID,
        isCSV=file.isCSV,
        isPDF=file.isPDF
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

# Read (모든 파일 조회)
def get_files(db: Session, skip: int = 0, limit: int = 10):
    return db.query(fileTBL).offset(skip).limit(limit).all()
# Read (특정 파일 조회)
def get_file_by_user_and_docs(db: Session, user_email: str, docs_id: str):
    return db.query(fileTBL).filter(
        fileTBL.userEmail == user_email,
        fileTBL.docsID == docs_id
    ).first()

# Update (파일 정보 수정)
def update_or_create_file(db: Session, file: FileCreate):
    # userEmail과 docsID로 기존 파일 검색
    db_file = db.query(fileTBL).filter(
        fileTBL.userEmail == file.userEmail,
        fileTBL.docsID == file.docsID
    ).first()

    if db_file:
        # 기존 파일 업데이트
        for key, value in file.dict().items():
            setattr(db_file, key, value)
        db.commit()
        db.refresh(db_file)
        return db_file

    # 새 파일 생성
    db_file = fileTBL(**file.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

# Delete (파일 삭제)
def delete_file(db: Session, file_id: int):
    db_file = db.query(fileTBL).filter(fileTBL.fileID == file_id).first()
    if not db_file:
        return False  # 파일 없음
    
    db.delete(db_file)
    db.commit()
    return True

# -------------------
# 질문 기록 생성
# -------------------
# Create (QnA 생성)
def create_qna(db: Session, qna: QnaCreate):
    db_qna = qnaTBL(**qna.dict())  # Pydantic 데이터를 SQLAlchemy 모델로 변환
    db.add(db_qna)
    db.commit()
    db.refresh(db_qna)  # 새로 생성된 객체 반환
    return db_qna

# Read (모든 QnA 조회)
def get_qnas(db: Session, skip: int = 0, limit: int = 10):
    return db.query(qnaTBL).offset(skip).limit(limit).all()

# Read (특정 QnA 조회)
def get_qna_by_id(db: Session, qna_id: int):
    return db.query(qnaTBL).filter(qnaTBL.qnaID == qna_id).first()

# Update (QnA 정보 수정)
def update_qna(db: Session, qna_id: int, updates: QnaUpdate):
    db_qna = db.query(qnaTBL).filter(qnaTBL.qnaID == qna_id).first()
    if not db_qna:
        return None  # QnA 없음

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_qna, key, value)  # 기존 QnA 객체에 업데이트 적용
    
    db.commit()
    db.refresh(db_qna)  # 업데이트된 객체 반환
    return db_qna

# Delete (QnA 삭제)
def delete_qna(db: Session, qna_id: int):
    db_qna = db.query(qnaTBL).filter(qnaTBL.qnaID == qna_id).first()
    if not db_qna:
        return False  # QnA 없음
    
    db.delete(db_qna)
    db.commit()
    return True

# -------------------
# csv 파일 CRUD
# -------------------
# Create (CSV 생성)
def create_csv(db: Session, csv: CsvCreate):
    db_csv = csvTBL(**csv.dict())  # Pydantic 데이터를 SQLAlchemy 모델로 변환
    db.add(db_csv)
    db.commit()
    db.refresh(db_csv)  # 새로 생성된 객체 반환
    return db_csv

# Read (모든 CSV 조회)
def get_csvs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(csvTBL).offset(skip).limit(limit).all()

# Read (특정 CSV 조회)
def get_csv_by_file_id(db: Session, file_id: int):
    return db.query(csvTBL).filter(csvTBL.fileID == file_id).first()

# Update (CSV 정보 수정)
def update_csv(db: Session, file_id: int, updates: CsvUpdate):
    db_csv = db.query(csvTBL).filter(csvTBL.fileID == file_id).first()
    if not db_csv:
        return None  # CSV 없음

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_csv, key, value)  # 기존 CSV 객체에 업데이트 적용
    
    db.commit()
    db.refresh(db_csv)  # 업데이트된 객체 반환
    return db_csv

# Delete (CSV 삭제)
def delete_csv(db: Session, file_id: int):
    db_csv = db.query(csvTBL).filter(csvTBL.fileID == file_id).first()
    if not db_csv:
        return False  # CSV 없음
    
    db.delete(db_csv)
    db.commit()
    return True

# -------------------
# pdf 파일 CRUD
# -------------------
# Create (PDF 생성)
def create_pdf(db: Session, pdf: PdfCreate):
    db_pdf = pdfTBL(**pdf.dict())  # Pydantic 데이터를 SQLAlchemy 모델로 변환
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)  # 새로 생성된 객체 반환
    return db_pdf

# Read (모든 PDF 조회)
def get_pdfs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(pdfTBL).offset(skip).limit(limit).all()

# Read (특정 PDF 조회)
def get_pdf_by_file_id(db: Session, file_id: int):
    return db.query(pdfTBL).filter(pdfTBL.fileID == file_id).first()

# Update (PDF 정보 수정)
def update_pdf(db: Session, file_id: int, updates: PdfUpdate):
    db_pdf = db.query(pdfTBL).filter(pdfTBL.fileID == file_id).first()
    if not db_pdf:
        return None  # PDF 없음

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_pdf, key, value)  # 기존 PDF 객체에 업데이트 적용
    
    db.commit()
    db.refresh(db_pdf)  # 업데이트된 객체 반환
    return db_pdf

# Delete (PDF 삭제)
def delete_pdf(db: Session, file_id: int):
    db_pdf = db.query(pdfTBL).filter(pdfTBL.fileID == file_id).first()
    if not db_pdf:
        return False  # PDF 없음
    
    db.delete(db_pdf)
    db.commit()
    return True