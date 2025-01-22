from fastapi import HTTPException, UploadFile
from dotenv import load_dotenv
import requests
import logging
import os
load_dotenv()
runpod_url = os.getenv("RUNPOD_URL")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------
# RunPod 통신 함수
# -------------------
def send_question_to_runpod(question: str, session_id: str, chat_option: str) -> str:
    """
    RunPod API와 통신하여 질문, session_id, chat_option을 전달하고 답변을 반환하는 함수.
    """

    # RunPod API URL
    url = f"https://{runpod_url}-8000.proxy.runpod.net/query/non-image"

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
    url = f"https://{runpod_url}-8000.proxy.runpod.net/query/image"

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
        # RunPod API URL
        url = f"https://{runpod_url}-8000.proxy.runpod.net/pdfs/upload"
        
        # 파일 경로에서 파일 읽기
        with open(file_path, "rb") as f:
            # files와 data 구성
            files = {
                "file": (os.path.basename(file_path), f, "application/pdf")
            }
            data = {"session_id": session_id}
            
            # 헤더 설정 (Content-Type은 requests가 자동으로 설정)
            headers = {
                "accept": "application/json"
            }
            
            # POST 요청 보내기
            response = requests.post(url, files=files, data=data, headers=headers)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 처리

        # 응답 처리
        response_data = response.json()
        if response_data.get("status") != "success":
            raise RuntimeError(f"RunPod API returned an error: {response_data}")

        return response_data

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to communicate with RunPod: {str(e)}")


def send_delete_pdf_request_to_runpod(file_name: str, session_id: str):
    """
    RunPod에 PDF 삭제 요청을 보내는 함수.
    """
    try:
        # RunPod API URL 설정 (curl 명령과 일치하도록 수정)
        url = f"https://{runpod_url}-8000.proxy.runpod.net/pdfs/delete"
        
        # 요청 페이로드와 헤더 구성
        payload = {
            "session_id": session_id,
            "file_name": file_name,
        }
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        # POST 요청 보내기
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리

        # 응답 처리
        response_data = response.json()
        if response_data.get("status") != "success":
            logger.error(f"RunPod API returned an error: {response_data}")
            raise RuntimeError(f"RunPod API returned an error: {response_data}")

        logger.info("Delete request successfully sent to RunPod")
        return response_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to communicate with RunPod: {str(e)}")
        raise RuntimeError(f"Failed to communicate with RunPod: {str(e)}")

# -------------------
# RunPod으로 CSV 파일 전송 함수
# -------------------
def send_csv_to_runpod(file: UploadFile, session_id: str):
    """
    RunPod으로 CSV 파일과 session_id를 전송하는 함수.
    """
    try:
        # RunPod API URL 설정
        url = f"https://{runpod_url}-8000.proxy.runpod.net/csvs/upload"
        logger.info(f"Sending CSV to RunPod: {file.filename}, session_id: {session_id}")

        # 파일 데이터를 multipart/form-data로 전송
        with file.file as f:
            files = {
                "file": (file.filename, f, file.content_type or "text/csv")
            }
            data = {"session_id": session_id}  # session_id를 데이터로 포함
            headers = {
                "accept": "application/json"
            }

            # POST 요청 보내기
            response = requests.post(url, files=files, data=data, headers=headers)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 처리

        # 응답 처리
        try:
            response_data = response.json()
        except ValueError:
            logger.error("Invalid JSON response from RunPod API")
            raise RuntimeError("Invalid JSON response from RunPod API")

        if response_data.get("status") != "success":
            logger.error(f"RunPod API returned an error: {response_data}")
            raise RuntimeError(f"RunPod API returned an error: {response_data}")

        logger.info("CSV successfully sent to RunPod")
        return response_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to communicate with RunPod: {str(e)}")
        raise RuntimeError(f"Failed to communicate with RunPod: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise RuntimeError(f"Unexpected error occurred: {str(e)}")
    

def send_delete_csv_request_to_runpod(file_name: str, session_id: str):
    """
    RunPod으로 CSV 삭제 요청을 보내는 함수.
    """
    try:
        # RunPod API URL 설정
        url = f"https://{runpod_url}-8000.proxy.runpod.net/csvs/delete"
        logger.info(f"Sending delete request to RunPod for file: {file_name}, session_id: {session_id}")

        # 요청 페이로드와 헤더 구성
        payload = {
            "session_id": session_id,
            "file_name": file_name,
        }
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        # POST 요청 보내기
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리

        # 응답 처리
        response_data = response.json()
        if response_data.get("status") != "success":
            logger.error(f"RunPod API returned an error: {response_data}")
            raise RuntimeError(f"RunPod API returned an error: {response_data}")

        logger.info("Delete request successfully sent to RunPod")
        return response_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to communicate with RunPod: {str(e)}")
        raise RuntimeError(f"Failed to communicate with RunPod: {str(e)}")