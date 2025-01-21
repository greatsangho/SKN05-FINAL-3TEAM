from fastapi import HTTPException, UploadFile
from dotenv import load_dotenv
import requests
import os
load_dotenv()

# -------------------
# RunPod 통신 함수
# -------------------
def send_question_to_runpod(question: str, session_id: str, chat_option: str) -> str:
    """
    RunPod API와 통신하여 질문, session_id, chat_option을 전달하고 답변을 반환하는 함수.
    """
    # 환경 변수 가져오기
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    api_key = os.getenv("RUNPOD_API_KEY")
    
    # 환경 변수 검증
    if not endpoint_id or not api_key:
        raise HTTPException(status_code=500, detail="RunPod API credentials are not set.")

    # RunPod API URL
    url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"

    # 요청 헤더
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json"
    }

    # 요청 바디
    body = {
        "input": {
            "question": question,
            "session_id": session_id,  # session_id 추가
            "chat_option": chat_option  # chat_option 추가
        }
    }

    # API 호출
    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # HTTP 상태 코드가 4xx/5xx인 경우 예외 발생
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"RunPod API request failed: {str(e)}")

    # 응답 처리
    try:
        output = response.json().get("output", {}).get("answer", "No answer received")
        return output
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"Invalid response format: {str(e)}")
  

# -------------------
# RunPod으로 PDF 파일 및 session_id 전송 함수
# -------------------
def send_pdf_to_runpod(file: UploadFile, session_id: str):
    """
    RunPod으로 PDF 파일과 session_id를 전송하는 함수.
    """
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    api_key = os.getenv("RUNPOD_API_KEY")
    
    # 환경 변수 검증
    if not endpoint_id or not api_key:
        raise HTTPException(status_code=500, detail="RunPod API credentials are not set.")

    try:
        url = f"https://api.runpod.ai/v2/{endpoint_id}/upload-pdf"  # RunPod API URL (예시)
        
        # 파일 데이터를 multipart/form-data로 전송
        with file.file as f:
            files = {"file": (file.filename, f, file.content_type)}
            data = {"session_id": session_id}  # session_id를 데이터로 포함
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.post(url, files=files, data=data, headers=headers)

        response.raise_for_status()  # 요청 실패 시 예외 발생

        return response.json()  # RunPod 응답 반환
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to communicate with RunPod: {str(e)}")
    
# -------------------
# RunPod으로 CSV 파일 전송 함수
# -------------------
def send_csv_to_runpod(file: UploadFile, session_id: str):
    """
    RunPod으로 CSV 파일과 session_id를 전송하는 함수.
    """
    try:
        runpod_url = "https://api.runpod.ai/v2/{endpoint_id}/upload-csv"  # RunPod API URL (예시)
        
        # 파일 데이터를 multipart/form-data로 전송
        with file.file as f:
            files = {"file": (file.filename, f, file.content_type)}
            data = {"session_id": session_id}  # session_id를 데이터로 포함
            response = requests.post(runpod_url, files=files, data=data)

        response.raise_for_status()  # 요청 실패 시 예외 발생

        return response.json()  # RunPod 응답 반환
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to communicate with RunPod: {str(e)}")
