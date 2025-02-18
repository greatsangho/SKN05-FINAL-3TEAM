---

# 🚀 FastAPI - Backend

이 프로젝트는 **FastAPI**를 기반으로 한 웹 애플리케이션 백엔드입니다.  
Google OAuth, 데이터베이스 연동, AI 통합, Docker 기반 배포 등 다양한 기능을 포함하고 있습니다.  
또한, SWAG(Nginx Reverse Proxy + Let's Encrypt)를 활용하여 HTTPS 지원 및 안정적인 배포 환경을 제공합니다.

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

이 프로젝트는 FastAPI를 활용하여 다음과 같은 주요 기능을 제공합니다:
- Google OAuth 데모 기능 (실제 운영에서는 Chrome Extension 인증으로 대체 가능).
- MySQL 데이터베이스와 SQLAlchemy ORM을 통한 데이터 관리.
- AI 플랫폼(RunPod)과의 통신을 통해 AI 기반 답변 생성.
- Docker와 SWAG(Nginx + Let's Encrypt)를 통한 컨테이너화 및 HTTPS 지원.
- 문서 편집 기능 제공(Google Docs API 연동).

---

## ✨ Features

- **OAuth Integration (Demo)**:  
  Google OAuth 데모 기능이 포함되어 있으며, 실제 인증은 Chrome Extension으로 수행.
  
- **MySQL Database Integration**:  
  SQLAlchemy를 활용하여 MySQL 데이터베이스와 연결, CRUD 작업 지원.

- **AI Integration**:  
  RunPod API를 통해 AI 기반 답변 생성 및 처리.

- **Docker Deployment**:  
  Docker와 Docker Compose를 사용하여 FastAPI와 SWAG(Nginx + Let's Encrypt) 컨테이너를 배포.

- **HTTPS & SSL Management**:  
  SWAG를 통해 HTTPS 지원 및 인증서 자동 갱신.

---

## 🗂 File Structure

```
Backend/
├── kubernetes/                  # Kubernetes 배포 관련 파일
│   └── finpilot-chart/          # Helm Chart 구성
│       ├── templates/           # Kubernetes 템플릿 파일
│       └── values.yaml          # Helm Chart 값 파일
├── sLLM/                        # AI 관련 모듈 및 API 서버
│   ├── finpilot_api_server_ollama_test/
│   │   ├── DB/                  # 데이터베이스 관련 코드
│   │   ├── Middleware/          # 미들웨어 구현
│   │   ├── finpilot/            # 주요 비즈니스 로직
│   │   ├── routers/             # API 라우터
│   │   └── main.py              # FastAPI 진입점
│   └── requirements.txt         # Python 의존성 목록
├── swag_fastapi_server/         # SWAG 기반 FastAPI 서버
│   ├── app/                     # FastAPI 애플리케이션 코드
│   │   ├── DB/                  # 데이터베이스 모델 및 스키마
│   │   ├── Middleware/          # 미들웨어 구현
│   │   ├── OAuth/               # OAuth 데모 코드
│   │   ├── Runpod/              # RunPod API 연동 모듈
│   │   └── routers/             # API 라우터 (users, sessions 등)
│   ├── nginx/                   # Nginx 설정 파일 (SWAG용)
│   └── docker-compose.yml       # Docker Compose 설정 파일
└── readme.md                    # 프로젝트 설명 문서
```

---

## 🛠 Technologies Used

- **Python**: 백엔드 개발 언어.
- **FastAPI**: 웹 프레임워크.
- **SQLAlchemy**: ORM 라이브러리 (MySQL 연동).
- **MySQL**: 관계형 데이터베이스.
- **Docker & Docker Compose**: 컨테이너화 및 배포 도구.
- **SWAG**: Nginx + Let's Encrypt로 HTTPS 지원.
- **RunPod API**: AI 플랫폼 연동.
- **Google Docs API**: 문서 편집 기능 제공.

---

## ⚙️ Setup and Installation

### Prerequisites

1. Python 3.10 이상 설치.
2. Docker 및 Docker Compose 설치.
3. MySQL 데이터베이스 준비.
4. DuckDNS 계정 생성 및 DUCKDNSTOKEN 확보(SWAG 인증서 발급용).

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
   `.env` 파일을 생성하고 아래 내용을 추가:
   ```
   GOOGLE_CLIENT_ID=<your_google_client_id>
   GOOGLE_CLIENT_SECRET=<your_google_client_secret>
   DATABASE_URL=mysql+pymysql://<USER>:<PASSWORD>@<HOST>:3306/<DATABASE_NAME>
   DUCKDNSTOKEN=<your_duckdns_token_here>
   ```

4. **Build & Run Docker Containers**
   ```bash
   docker-compose up -d --build
   ```

---

## 🚀 How to Run

1. **Docker 기반 실행**
    - `docker-compose up -d` 명령어로 컨테이너 실행.
    - 브라우저에서 `https://finpilotback.duckdns.org`로 접속.

2. **로컬 개발 실행**
    ```bash
    uvicorn app.main:app --reload
    ```
    - Swagger UI 확인: `http://127.0.0.1:8000/docs`.

3. **Test Endpoints**
    - `/health`: 서버 상태 확인.
    - `/auth/google`: Google OAuth 데모 테스트.
    - 기타 라우터(users, sessions 등) 테스트.

---

## 🐳 Docker Implementation

### Dockerfile

Python 3.11-slim 이미지를 기반으로 FastAPI 애플리케이션 빌드.

### docker-compose.yml

FastAPI와 SWAG(Nginx + Let's Encrypt)를 하나의 네트워크에서 실행:
1. SWAG는 DuckDNS를 통해 HTTPS 인증서를 발급받음.
2. Nginx가 트래픽을 FastAPI로 프록시.

---

## 🤝 Contribution

1. Fork this repository.
2. Create a new branch:
    ```bash
    git checkout -b feature/new-feature
    ```
3. Commit your changes:
    ```bash
    git commit -m "Add new feature"
    ```
4. Push to the branch:
    ```bash
    git push origin feature/new-feature
    ```
5. Open a Pull Request.

---

## 📧 Contact

- Email: greatsangho@gmail.com  
- GitHub: [https://github.com/greatsangho](https://github.com/greatsangho)