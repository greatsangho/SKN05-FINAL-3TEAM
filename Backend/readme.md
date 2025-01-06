# 🚀 FastAPI - Backend

이 프로젝트는 **FastAPI**를 기반으로 한 웹 애플리케이션 백엔드입니다. OAuth를 통한 Google 인증, Google Docs API 통합, 데이터베이스 CRUD 기능, 그리고 외부 AI 서비스와의 통신을 포함한 다양한 기능을 제공합니다.

---

## 📖 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [File Structure](#-file-structure)
- [Technologies Used](#-technologies-used)
- [Setup and Installation](#-setup-and-installation)
- [How to Run](#-how-to-run)
- [Contribution](#-contribution)

---

## 📋 About the Project

이 프로젝트는 Google OAuth를 통해 사용자를 인증하고, Google Docs API를 활용하여 문서를 편집하며, 데이터베이스를 통해 질문/답변 데이터를 관리합니다. 또한, 외부 AI 플랫폼인 RunPod와 통합하여 질문에 대한 답변을 생성합니다.

---

## ✨ Features

- **OAuth Integration**: Google 계정을 통한 인증 및 사용자 정보 관리.
- **Google Docs API**: 문서 수정 및 업데이트 기능 제공.
- **Database Management**:
  - 질문/답변 데이터 저장 및 CRUD 기능.
  - SQLAlchemy ORM을 사용한 데이터베이스 모델링.
- **AI Integration**: RunPod API를 통해 질문에 대한 AI 기반 답변 생성.
- **Error Handling**: HTTPException을 활용한 상세한 에러 처리.

---

## 🗂 File Structure

```
backend/
├── main.py                   # FastAPI 애플리케이션 메인 파일
├── models.py                 # SQLAlchemy 데이터베이스 모델 정의
├── schemas.py                # Pydantic 모델 정의
├── database.py               # 데이터베이스 설정 및 의존성 관리
├── auth.py                   # OAuth 및 인증 관련 로직
├── google_docs.py            # Google Docs API 통합 로직
├── runpod.py                 # RunPod API 통신 로직
└── .env                      # 환경 변수 파일 (Google OAuth 및 DB 설정)
```

---

## 🛠 Technologies Used

Python
FastAPI
SQLAlchemy
Google Docs API
RunPod API

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.10 이상
- MySQL 데이터베이스
- Google Cloud Platform에서 OAuth 클라이언트 ID 및 비밀키 생성

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/greatsangho/your-repo.git
   cd your-repo/backend
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**
   `.env` 파일을 생성하고 아래 내용을 추가:
   ```
   GOOGLE_CLIENT_ID=<your_google_client_id>
   GOOGLE_CLIENT_SECRET=<your_google_client_secret>
   REDIRECT_URI=<your_redirect_uri>
   DATABASE_URL=mysql+pymysql://<USER>:<PASSWORD>@<HOST>:3306/<DATABASE_NAME>
   ```

4. **Run Database Migrations**
   ```bash
   python main.py
   ```

---

## 🚀 How to Run

1. **Start the Server**
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the API Documentation**
   - 브라우저에서 `http://127.0.0.1:8000/docs`로 이동하여 Swagger UI 확인.

3. **Test OAuth Login**
   - `/auth/google` 엔드포인트로 이동하여 Google 로그인 테스트.

4. **Test CRUD Operations**
   - `/questions` 엔드포인트에서 질문 생성, 조회, 수정, 삭제 테스트.

5. **Test Google Docs Integration**
   - `/edit_doc` 엔드포인트로 문서 수정 테스트.

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

> 이 README는 FastAPI 백엔드 프로젝트에 최적화된 문서입니다. 전체 프로젝트에 대한 자세한 내용은 메인 브랜치의 README를 참조하세요.

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/31113019/709cf0d8-70ee-4202-9fc2-6b5a06c0851a/paste.txt