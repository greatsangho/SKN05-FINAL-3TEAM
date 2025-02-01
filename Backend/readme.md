---

# 🚀 FastAPI - Backend

이 프로젝트는 **FastAPI**를 기반으로 한 웹 애플리케이션 백엔드입니다.  
Google OAuth 기능이 데모로 구현되어 있으나, 실제 운영에서는 MySQL 데이터베이스와 모델 연동을 위해 사용됩니다. 또한, Docker 환경에서 컨테이너화된 FastAPI 애플리케이션을 SWAG(Nginx Reverse Proxy + Let's Encrypt)와 함께 운영하여, 안정적인 배포와 SSL 인증서 자동 갱신 등의 기능을 제공합니다.

---

## 📖 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [File Structure](#-file-structure)
- [Technologies Used](#-technologies-used)
- [Setup and Installation](#-setup-and-installation)
- [How to Run](#-how-to-run)
- [Docker Implementation](#-docker-implementation)
- [Contribution](#-contribution)
- [Contact](#-contact)

---

## 📋 About the Project

이 프로젝트는 FastAPI 백엔드 애플리케이션의 다양한 기능들을 제공합니다.  
- Google OAuth 기능은 웹서버 용으로 구현되어 있으며, 실제로는 Chrome Extention으로 구현하였기 때문에 웹서버에 사용할 때 참고할 수 있도록 코드를 남겨두었습니다.
- 데이터베이스와 SQLAlchemy 모델을 연결은 FastAPI 서버에서 수행합니다.
- 데이터베이스 CRUD 작업, 외부 AI 플랫폼(RunPod)과의 통신, 그리고 Google Docs API 연동(문서 편집) 기능 등이 포함되어 있습니다.  
- Docker와 Docker Compose를 이용하여 FastAPI와 SWAG(Nginx + Let's Encrypt)를 한 번에 배포할 수 있도록 구성하였습니다.

---

## ✨ Features

- **OAuth Integration (Demo)**:  
  Google OAuth 기능이 포함되어 있으나, 실제 인증은 Chrome Extention으로 진행하는 것으로 변경 및 이관.  
- **MySQL Database & Model Integration**:  
  SQLAlchemy를 활용하여 MySQL 데이터베이스에 연결하고, CRUD 작업을 수행하며, 데이터 모델을 관리합니다.
- **Google Docs API Integration**:  
  문서 수정 및 업데이트 기능을 제공 (선택적 기능).
- **AI Integration**:  
  RunPod API를 통해 AI 기반 답변 생성을 지원합니다.
- **Docker Deployment**:  
  Dockerfile과 docker-compose.yml을 사용하여 FastAPI와 SWAG(Nginx + Let's Encrypt) 컨테이너를 손쉽게 배포할 수 있으며, 이를 통해 HTTPS와 자동 인증서 갱신 기능을 제공합니다.
- **Error Handling**:  
  FastAPI의 HTTPException을 활용한 에러 처리 로직이 구현되어 있습니다.

---

## 🗂 File Structure

```
backend/
├── Dockerfile                   # FastAPI 애플리케이션 Docker 이미지 빌드 파일 (Python 3.11-slim 기반)
├── docker-compose.yml           # FastAPI 및 SWAG 컨테이너 실행을 위한 Docker Compose 파일
├── readme.md                    # 이 문서
├── app/                         
│   ├── __init__.py              
│   ├── main.py                  # FastAPI 진입점, 라우터 포함, 모델 및 DB 설정
│   ├── requirements.txt         # 필수 Python 라이브러리 목록
│   ├── DB/                      # ORM 모델, CRUD 및 데이터베이스 관련 파일
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── ERD/finpilot.mwb      # 데이터베이스 ERD 파일 (MySQL Workbench)
│   ├── Middleware/              # 커스텀 미들웨어 관련 파일
│   ├── OAuth/                   # Google OAuth 관련 데모 기능 (실제 운영에서는 DB 연동 용도)
│   ├── Helper/                  # 보조 유틸리티 함수
│   ├── Runpod/                  # RunPod API 통신 로직
│   └── routers/                 # 각종 API 엔드포인트 라우터 (users, sessions, qnas, pdfs, csvs 등)
├── nginx/                       
│   └── site-confs/              
│       └── finpilotback.duckdns.org.conf  # SWAG용 Nginx 설정 파일: finpilotback.duckdns.org로 트래픽을 FastAPI에 프록시
└── 기타 (캐시 디렉토리 등)
```

---

## 🛠 Technologies Used

- **Python**: 프로그래밍 언어
- **FastAPI**: 웹 프레임워크
- **SQLAlchemy**: ORM (MySQL 연동)
- **MySQL**: 데이터베이스
- **Docker & Docker Compose**: 컨테이너 기반 배포
- **SWAG**: LinuxServer SWAG (Nginx + Let's Encrypt) – HTTPS 및 인증서 관리
- **Google Docs API**: 문서 편집 연동 (선택적)
- **RunPod API**: AI 답변 생성 기능

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.10 이상
- Docker 및 Docker Compose 설치
- MySQL 데이터베이스 (로컬 또는 원격)
- Google Cloud Platform에서 OAuth 클라이언트 ID (데모용)
- DuckDNS 계정 및 DUCKDNSTOKEN (SWAG 인증서 발급용)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/greatsangho/your-repo.git
   cd your-repo/backend
   ```

2. **Install Dependencies (로컬 개발 시)**
   ```bash
   pip install -r app/requirements.txt
   ```

3. **Set Up Environment Variables**  
   프로젝트 루트 또는 app 폴더에 `.env` 파일을 생성하고 아래 내용을 추가:
   ```
   GOOGLE_CLIENT_ID=<your_google_client_id>
   GOOGLE_CLIENT_SECRET=<your_google_client_secret>
   REDIRECT_URI=<your_redirect_uri>
   DATABASE_URL=mysql+pymysql://<USER>:<PASSWORD>@<HOST>:3306/<DATABASE_NAME>
   DUCKDNSTOKEN=<your_duckdns_token_here>
   ```
   > Google OAuth는 데모용 기능이며, 실제 운영에서는 MySQL 데이터베이스 연결과 모델 관리를 위한 설정이 주를 이룹니다.

4. **Build & Run Docker Containers**
   ```bash
   docker-compose down
   docker-compose up -d
   ```
   - FastAPI와 SWAG(Nginx 및 Let’s Encrypt)가 동일 네트워크(app-network)에서 실행됩니다.
   - SWAG는 DuckDNS를 통해 `finpilotback.duckdns.org` 도메인에 대해 인증서를 발급받고, 해당 트래픽을 FastAPI 서버(8000 포트)로 프록시합니다.

---

## 🚀 How to Run

1. **Docker 기반 실행 시**
   - 위의 `docker-compose up -d` 명령어로 컨테이너를 실행합니다.
   - 도메인 `https://finpilotback.duckdns.org`에 접속하면 SWAG Nginx가 HTTPS 트래픽을 FastAPI 서버로 전달합니다.

2. **로컬 개발 시**
   ```bash
   uvicorn app.main:app --reload
   ```
   - 브라우저에서 `http://127.0.0.1:8000/docs`로 이동하여 Swagger UI를 확인합니다.

3. **Test Endpoints**
   - `/health` 엔드포인트로 서버 상태 확인
   - `/auth/google` (데모용) 엔드포인트로 Google OAuth 기능 확인
   - 기타 라우터 엔드포인트 (users, sessions, qnas, pdfs, csvs)로 CRUD 및 연동 기능 테스트

---

## 🐳 Docker Implementation Details

- **Dockerfile**  
  - Python 3.11-slim 이미지를 기반으로 하며, 필요한 패키지 설치와 FastAPI 애플리케이션 코드를 컨테이너에 복사합니다.
  - Uvicorn을 이용해 FastAPI 서버를 실행하며, `--proxy-headers` 옵션으로 클라이언트 IP 및 헤더 정보를 올바르게 전달합니다.

- **docker-compose.yml**  
  - FastAPI와 SWAG 컨테이너를 같은 Docker 네트워크(app-network)에 연결하여 서로 통신할 수 있도록 구성합니다.
  - FastAPI 컨테이너는 8000번 포트를 외부에 노출하며, 등록된 healthcheck를 통해 상태를 주기적으로 확인합니다.
  - SWAG 컨테이너는 DuckDNS를 통한 인증서 발급을 위해 환경 변수를 설정하며, Nginx 설정 파일(`finpilotback.duckdns.org.conf`)을 통해 `finpilotback.duckdns.org` 도메인의 HTTP/HTTPS 트래픽을 FastAPI 컨테이너로 프록시합니다.
  - SWAG는 Let's Encrypt 인증서를 `/config/etc/letsencrypt/live/finpilotback.duckdns.org`에 저장하고, Nginx 설정 파일에서는 이를 참조하도록 경로를 `/config/etc/letsencrypt/live/...`로 지정합니다.

---

## 🤝 Contribution

1. **Fork this repository**.
2. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Commit your changes**:
   ```bash
   git commit -m "Add new feature"
   ```

4. **Push to the branch**:
   ```bash
   git push origin feature/your-feature
   ```

5. **Open a Pull Request**.

---

## 📧 Contact

- **Email**: greatsangho@gmail.com
- **GitHub**: [https://github.com/greatsangho](https://github.com/greatsangho)

---

> 이 README는 FastAPI 백엔드 프로젝트와 Docker, SWAG를 통한 배포 환경을 상세하게 설명하고 있습니다.  
> 전체 프로젝트에 대한 자세한 내용은 메인 브랜치의 README를 참조하세요.

Citations:  
 https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/31113019/709cf0d8-70ee-4202-9fc2-6b5a06c0851a/paste.txt