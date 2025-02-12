from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB import schemas, crud
from DB.database import get_db

router = APIRouter()

# -------------------
# 세션 정보 CRUD 엔드포인트
# -------------------
@router.post("/", response_model=schemas.SessionID)
def create_session(session_data: schemas.SessionIDBase, db: Session = Depends(get_db)):
    try:
        # Check if the session already exists or create a new one
        new_session = crud.create_session(
            db=db,
            user_email=session_data.user_email,
            docs_id=session_data.docs_id,
        )
        return new_session
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))  # Handle invalid input
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/", response_model=list[schemas.SessionID])
def read_sessions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db=db, skip=skip, limit=limit)
    return sessions

@router.get("/{session_id}", response_model=schemas.SessionID)
def read_session(session_id: str, db: Session = Depends(get_db)):
    session = crud.get_session_by_id(db=db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    success = crud.delete_session(db=db, session_id=session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}
