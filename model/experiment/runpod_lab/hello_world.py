# 서버리스 애플리케이션을 만들고 관리하는 데 필요한 모든 도구 임포트
import runpod

def handler(job):
    job_input = job["input"]

    return f"Hello {job_input['name']}!"

# 서버리스 워커 시작
# 들어오는 작업을 처리할 준비를 함
runpod.serverless.start({"handler" : handler})