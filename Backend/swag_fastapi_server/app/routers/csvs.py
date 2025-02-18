from fastapi import APIRouter, Depends, HTTPException
from fastapi import File, UploadFile, Form
from Runpod.runpod import send_csv_to_runpod, send_delete_csv_request_to_runpod
from sqlalchemy.orm import Session
from DB import crud
from DB import models
from DB.database import get_db


router = APIRouter()

# -------------------
# CSV 파일 업로드 엔드포인트
# -------------------
@router.post("/")
async def upload_csv(
    user_email: str = Form(...),
    docs_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    클라이언트가 업로드한 CSV 파일과 함께 user_email 및 docs_id를 받아서,
    session_id와 파일을 RunPod으로 전송.
    """
    try:
        # 1. 파일 형식 확인 (CSV만 허용)
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

        # 2. 세션 확인 또는 생성
        session = crud.create_session(db=db, user_email=user_email, docs_id=docs_id)
        session_id = session.session_id  # 세션 ID 가져오기

        # 3. RunPod으로 파일과 session_id 전송
        runpod_response = send_csv_to_runpod(file=file, session_id=session_id)

        # 4. RunPod 응답 반환
        if runpod_response.get("status") != "success":
            raise HTTPException(status_code=502, detail="Failed to process CSV file with RunPod")

        return {
            "message": "CSV file processed successfully",
            "session_id": session_id,
            "runpod_response": runpod_response,
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# -------------------
# CSV 파일 삭제 엔드포인트
# -------------------
@router.delete("/")
async def delete_csv(
    user_email: str = Form(...),
    docs_id: str = Form(...),
    file_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    클라이언트가 요청한 user_email, docs_id, file_name을 받아서,
    RunPod에 삭제 요청을 보냄.
    """
    try:
        # 1. 세션 확인 또는 생성
        session = crud.create_session(db=db, user_email=user_email, docs_id=docs_id)
        session_id = session.session_id  # 세션 ID 가져오기

        # 2. RunPod으로 삭제 요청 전송
        runpod_response = send_delete_csv_request_to_runpod(file_name=file_name, session_id=session_id)

        # 3. RunPod 응답 확인
        if runpod_response.get("status") != "success":
            raise HTTPException(status_code=502, detail="Failed to delete CSV file with RunPod")

        return {
            "message": "CSV file deleted successfully",
            "runpod_response": runpod_response,
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
