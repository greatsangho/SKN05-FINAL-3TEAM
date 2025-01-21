from fastapi import HTTPException, UploadFile
from dotenv import load_dotenv
import requests
import os
load_dotenv()
runpod_url = os.getenv("RUNPOD_URL")
# -------------------
# RunPod 통신 함수
# -------------------
def send_question_to_runpod(question: str, session_id: str, chat_option: str) -> str:
    """
    RunPod API와 통신하여 질문, session_id, chat_option을 전달하고 답변을 반환하는 함수.
    """

    # RunPod API URL
    url = f"https://{runpod_url}-8000.proxy.runpod.net/query"

    # 요청 헤더
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    # 요청 바디
    body = {
        "session_id": session_id,
        "question": question,
        "chat_option": chat_option
    }

    # API 호출
    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # HTTP 상태 코드가 4xx/5xx인 경우 예외 발생
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"RunPod API request failed: {str(e)}")

    # 응답 처리
    try:
        output = response.json().get("answer", "No answer received")
        return output
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"Invalid response format: {str(e)}")
  
def send_graph_to_runpod(question: str, session_id: str, chat_option: str) -> list:
    """
    RunPod API와 통신하여 그래프 요청을 보내고 base64 이미지 리스트를 반환하는 함수.
    """
    # RunPod API URL
    url = f"https://{runpod_url}-8000.proxy.runpod.net/get-graph-image"

    # 요청 헤더
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    # 요청 바디
    body = {
        "session_id": session_id,
        "question": question,
        "chat_option": chat_option
    }

    # API 호출
    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()  # HTTP 상태 코드가 4xx/5xx인 경우 예외 발생
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"RunPod API request failed: {str(e)}")

    # 응답 처리
    try:
        output = response.json()
        images = output.get("images", [])
        return images  # 이미지 리스트 반환 (file_name과 image_data 포함)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"Invalid response format: {str(e)}")
# -------------------
# RunPod으로 PDF 파일 및 session_id 전송 함수
# -------------------
def send_pdf_to_runpod(file_path: str, session_id: str):
    """
    RunPod으로 PDF 파일 경로와 session_id를 전송하는 함수.
    """
    try:
        url = f"https://{runpod_url}-8000.proxy.runpod.net/upload-pdf"
        
        # 파일 경로에서 파일 읽기
        with open(file_path, "rb") as f:
            files = {
                "file": (os.path.basename(file_path), f, "application/pdf")
            }
            data = {"session_id": session_id}
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }
            response = requests.post(url, files=files, data=data, headers=headers)
            response.raise_for_status()

        response_data = response.json()
        if response_data.get("status") != "success":
            raise RuntimeError(f"RunPod API returned an error: {response_data}")

        return response_data

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
        url = f"https://{runpod_url}-8000.proxy.runpod.net/upload-csv"
        
        # 파일 데이터를 multipart/form-data로 전송
        with file.file as f:
            files = {"file": (file.filename, f, file.content_type)}
            data = {"session_id": session_id}  # session_id를 데이터로 포함
            response = requests.post(url, files=files, data=data)

        response.raise_for_status()  # 요청 실패 시 예외 발생

        return response.json()  # RunPod 응답 반환
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to communicate with RunPod: {str(e)}")


def send_delete_csv_request_to_runpod(file_name: str, session_id: str):
    try:
        # Replace with your actual RunPod API endpoint and authentication details
        url = f"https://{runpod_url}-8000.proxy.runpod.net/delete-pdf"
        payload = {
            "session_id": session_id,
            "file_name": file_name,
        }
        headers = {
            # "Authorization": "Bearer YOUR_RUNPOD_API_KEY",  # Replace with your API key
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error sending delete request to RunPod: {e}")
        return {"status": "error", "message": str(e)}