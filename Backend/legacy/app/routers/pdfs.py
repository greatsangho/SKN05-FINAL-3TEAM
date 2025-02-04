from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB import schemas, crud
from DB.database import get_db
from Runpod.runpod import send_pdf_to_runpod, send_delete_pdf_request_to_runpod
from fastapi import File, UploadFile, Form
import shutil
import os

router = APIRouter()

# -------------------
# PDF 파일 CRUD 엔드포인트
# -------------------

@router.post("/", response_model=schemas.PDFFile)
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

        # 3. PDF 파일 정보 생성 및 저장 (파일 이름만 저장)
        new_pdf_file = crud.create_pdf_file(
            db=db,
            user_email=user_email,
            docs_id=docs_id,
            file_name=file.filename,
        )

        # 4. RunPod으로 파일과 session_id 전송
        runpod_response = send_pdf_to_runpod(file_path=file_path, session_id=session_id)

        # 5. RunPod 응답 확인 및 반환
        if runpod_response.get("status") != "success":
            raise HTTPException(status_code=502, detail="Failed to process file with RunPod")

        return new_pdf_file
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/", response_model=list[schemas.PDFFile])
def read_pdfs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    pdfs = crud.get_pdfs(db=db, skip=skip, limit=limit)
    return pdfs

@router.delete("/")
async def delete_pdf(
    user_email: str = Form(...),
    docs_id: str = Form(...),
    file_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    PDF 삭제 엔드포인트:
    1. RunPod에 PDF 삭제 요청 전송.
    2. 데이터베이스에서 PDF 파일 정보 확인 및 삭제.
    """
    try:
        # 1. 세션 확인 또는 생성
        session = crud.create_session(db=db, user_email=user_email, docs_id=docs_id)
        session_id = session.session_id  # 세션 ID 가져오기

        # 2. RunPod에 PDF 삭제 요청 전송
        runpod_response = send_delete_pdf_request_to_runpod(
            file_name=file_name,
            session_id=session_id
        )

        # 3. RunPod 응답 확인
        if runpod_response.get("status") != "success":
            raise HTTPException(status_code=502, detail="Failed to delete PDF file on RunPod")

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

        return {"message": "PDF file deleted successfully", "runpod_response": runpod_response}

    except HTTPException as http_exc:
        raise http_exc  # FastAPI HTTP 예외는 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
