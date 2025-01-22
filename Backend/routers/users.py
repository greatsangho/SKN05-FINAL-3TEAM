from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB import schemas, crud
from DB.database import get_db
from datetime import datetime, timezone

router = APIRouter()
# -------------------
# 유저 정보 CRUD 엔드포인트
# -------------------
@router.post("/", response_model=schemas.Member)
def create_or_update_user(user: schemas.MemberBase, db: Session = Depends(get_db)):
    # 현재 시간을 UTC로 설정
    current_time = datetime.now(timezone.utc)

    # 기존 유저 확인
    existing_user = crud.get_user_by_email(db=db, user_email=user.user_email)
    if existing_user:
        # 기존 유저 로그인 시간 업데이트
        updated_user = crud.update_user_login_time(db=db, user_email=user.user_email)
        return updated_user

    # 새로운 유저 생성
    new_user = crud.create_user(db=db, user_email=user.user_email)
    return new_user

@router.delete("/{user_email}")
def delete_user(user_email: str, db: Session = Depends(get_db)):
    result = crud.delete_user(db=db, user_email=user_email)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}