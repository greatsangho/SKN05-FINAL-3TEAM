from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB import schemas, crud
from DB.database import get_db
from Runpod.runpod import send_question_to_runpod, send_graph_to_runpod
from DB import schemas, crud, models
from typing import List

router = APIRouter()

# -------------------
# 질문 기록 CRUD 엔드포인트 및 RunPod 연동
# -------------------
@router.post("/", response_model=schemas.QnA)
def create_qna(qna: schemas.QnACreate, db: Session = Depends(get_db)):
    """
    QnA 생성 엔드포인트:
    1. 세션 확인 또는 생성
    2. RunPod 호출 (질문과 session_id 전달)
    3. QnA 데이터 생성 및 저장
    """
    try:
        # 1. 세션이 존재하는지 확인하거나 생성
        session = crud.create_session(
            db=db,
            user_email=qna.user_email,
            docs_id=qna.docs_id,
        )

        # 2. RunPod 호출 (외부 서비스 연동) - chat_option에 따라 다른 함수 호출
        try:
            if "데이터 시각화" in qna.chat_option:
                # 데이터 시각화 요청인 경우 send_graph_to_runpod 호출
                graph_response = send_graph_to_runpod(
                    question=qna.question,
                    session_id=session.session_id,
                    chat_option=qna.chat_option
                )
                # RunPod에서 반환된 그래프 데이터를 처리 ("images":[{},{}] 형태로 저장)
                # answer = {"images": graph_response} # 바꾸기
                answer = graph_response
            else:
                # 일반 질문 처리
                answer = send_question_to_runpod(
                    question=qna.question,
                    session_id=session.session_id,
                    chat_option=qna.chat_option
                )
        except Exception as e:
            raise HTTPException(status_code=502, detail="Failed to communicate with RunPod")

        # 3. QnA 데이터 생성 및 저장 (session_id 및 chat_option 포함)
        new_qna = crud.create_qna(
            db=db,
            user_email=qna.user_email,
            docs_id=qna.docs_id,
            question=qna.question,
            session_id=session.session_id,
            chat_option=qna.chat_option,  # chat_option 명시적으로 전달
        )
        
        # 4. RunPod에서 받은 답변을 QnA에 추가
        new_qna.answer = answer
        db.commit()
        db.refresh(new_qna)

        return new_qna

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))  # 잘못된 입력 처리
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/", response_model=List[schemas.QnA])
def get_qnas(user_email: str, docs_id: str, db: Session = Depends(get_db)):
    """
    QnA 조회 엔드포인트:
    - user_email과 docs_id를 기반으로 저장된 QnA 데이터를 반환
    """
    try:
        # 데이터베이스에서 해당 user_email과 docs_id에 해당하는 QnA 검색
        qnas = db.query(models.QnA).filter(
            models.QnA.user_email == user_email,
            models.QnA.docs_id == docs_id
        ).all()

        # 결과가 없을 경우 예외 처리
        if not qnas:
            raise HTTPException(status_code=404, detail="No QnA found for the given user_email and docs_id.")

        return qnas

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.delete("/{qna_id}")
def delete_qna(qna_id: int, db: Session = Depends(get_db)):
    """
    QnA 삭제 엔드포인트:
    - qna_id를 기반으로 특정 QnA 데이터를 삭제.
    """
    try:
        # QnA 데이터베이스에서 qna_id로 검색
        qna = crud.get_qna_by_id(db=db, qna_id=qna_id)
        if not qna:
            raise HTTPException(status_code=404, detail="QnA not found")

        # QnA 데이터 삭제
        success = crud.delete_qna(db=db, qna_id=qna_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete QnA")

        return {"message": "QnA deleted successfully"}
    
    except HTTPException as http_exc:
        raise http_exc  # FastAPI HTTP 예외는 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
