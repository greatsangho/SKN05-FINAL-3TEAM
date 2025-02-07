from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DB import schemas, crud
from DB.database import get_db
from DB import schemas, crud
from .response.query import query_non_image, query_image
import pickle

qna_router = APIRouter()

# -------------------
# 질문 기록 CRUD 엔드포인트 및 모델 연동
# -------------------
# @router.post("/", response_model=schemas.QnA)
@qna_router.post("/")
async def create_qna(qna: schemas.QnACreate, db: Session = Depends(get_db)):
    """
    QnA 생성 엔드포인트:
    1. 세션 확인 또는 생성
    2. 모델 호출 (질문과 session_id 전달)
    3. QnA 데이터 생성 및 저장
    """
    try:
        # 1. 세션이 존재하는지 확인하거나 생성
        session = crud.create_session(
            db=db,
            user_email=qna.user_email,
            docs_id=qna.docs_id,
        )

        # 2. 모델 호출 (외부 서비스 연동) - chat_option에 따라 다른 함수 호출
        try:
            if "데이터 시각화" in qna.chat_option:
                # 데이터 시각화 요청인 경우 query_image 호출
                graph_response = await query_image(
                    question=qna.question,
                    session_id=session.session_id,
                    chat_option=qna.chat_option,
                    pilot=qna_router.pilot
                )
                
                # 모델에서 반환된 전체 JSON 응답 저장
                answer = graph_response  # 전체 JSON 그대로 저장
                
            else:
                # 일반 질문 처리
                answer = await query_non_image(
                    question=qna.question,
                    session_id=session.session_id,
                    chat_option=qna.chat_option,
                    pilot=qna_router.pilot
                )

                # 3. QnA 데이터 생성 및 저장 (session_id 및 chat_option 포함)
                new_qna = crud.create_qna(
                    db=db,
                    user_email=qna.user_email,
                    docs_id=qna.docs_id,
                    question=qna.question,
                    session_id=session.session_id,
                    chat_option=qna.chat_option,
                    source=answer["source"],
                    answer=answer["answer"]
                )
                
                return new_qna  # 프론트엔드로 그대로 전달
            
        except Exception as e:
            raise HTTPException(status_code=502, detail="Failed to invoke the model: " + str(e))
        
        return answer

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))  # 잘못된 입력 처리
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")