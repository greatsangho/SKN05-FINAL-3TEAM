from fastapi import HTTPException
from dotenv import load_dotenv
import requests
import os
load_dotenv()
# -------------------
# RunPod 통신 함수
# -------------------
def send_to_runpod(question: str) -> str:
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
            "question": question
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
        output = response.json().get("output", {}).get("finpilot_answer", "No answer received")
        return output
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"Invalid response format: {str(e)}")