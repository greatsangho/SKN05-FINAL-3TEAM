from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB import schemas, crud
from DB.database import get_db
from fastapi import File, UploadFile, Form
import shutil
import os
from .response.pdfs import upload_pdfs, delete_pdfs

pdfs_router = APIRouter()

# -------------------
# PDF 파일 CRUD 엔드포인트
# -------------------

@pdfs_router.post("/", response_model=schemas.PDFFile)
async def create_pdf(
    user_email: str = Form(...),
    docs_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # 1. 세션 확인 또는 생성
        session = crud.create_session(db=db, user_email=user_email, docs_id=docs_id)
        session_id = session.session_id

        # 2. 파일 저장 (임시 디렉토리 사용)
        temp_dir = "/tmp/pdf_files"
        os.makedirs(temp_dir, exist_ok=True)  # 디렉토리가 없으면 생성
        file_path = os.path.join(temp_dir, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)  # 파일 저장

        # 파일 저장 후, 파일 포인터를 처음 위치로 재설정해야 다음 과정에서 파일을 올바르게 읽을 수 있습니다.
        file.file.seek(0)

        # 3. PDF 파일 정보 생성 및 저장 (파일 이름만 저장)
        new_pdf_file = crud.create_pdf_file(
            db=db,
            user_email=user_email,
            docs_id=docs_id,
            file_name=file.filename,
        )

        # 4. VertorDB에 저장
        pdfs_router.vector_store = await upload_pdfs(file=file, session_id=session_id, vector_store=pdfs_router.vector_store)

        return new_pdf_file

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@pdfs_router.get("/", response_model=list[schemas.PDFFile])
def read_pdfs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    pdfs = crud.get_pdfs(db=db, skip=skip, limit=limit)
    return pdfs

@pdfs_router.delete("/")
async def delete_pdf(
    user_email: str = Form(...),
    docs_id: str = Form(...),
    file_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    PDF 삭제 엔드포인트:
    1. Vector Store에서 PDF 파일 삭제.
    2. 데이터베이스에서 PDF 파일 정보 확인 및 삭제.
    """
    try:
        # 1. 세션 확인 또는 생성
        session = crud.create_session(db=db, user_email=user_email, docs_id=docs_id)
        session_id = session.session_id  # 세션 ID 가져오기

        # 2. Vector Store에서 PDF 파일 삭제
        pdfs_router.vector_store = await delete_pdfs(
            file_name=file_name,
            session_id=session_id,
            vector_store=pdfs_router.vector_store
        )

        # 4. 데이터베이스에서 PDF 파일 확인
        pdf_file = crud.get_pdf_file(
            db=db,
            user_email=user_email,
            docs_id=docs_id,
            file_name=file_name
        )
        if not pdf_file:
            raise HTTPException(status_code=404, detail="PDF file not found")

        # 5. 데이터베이스에서 PDF 파일 삭제
        success = crud.delete_pdf_file(db=db, pdf_id=pdf_file.pdf_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete PDF file from database")

        return {"message": "PDF file deleted successfully"}

    except HTTPException as http_exc:
        raise http_exc  # FastAPI HTTP 예외는 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
