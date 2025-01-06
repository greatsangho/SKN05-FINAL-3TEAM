# 🚀 FinPilot - Frontend

FinPilot은 Google Docs와 원활하게 통합된 SLLM 기반 Chrome Extension입니다. 

**Frontend**는 사용자가 직관적으로 접근할 수 있는 사용자 인터페이스를 제공하며, SLLM을 활용하여 금융 문서 생성 및 편집을 돕습니다.

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

FinPilot은 Google Docs 환경에서 사용자가 더 효율적으로 금융 문서를 작성하고 관리할 수 있도록 설계된 **Chrome Extension**입니다. 
이 프로젝트는 **AI 기반 텍스트 생성**과 **Google Docs 통합**을 핵심 기능으로 제공합니다.

---

## ✨ Features

- **AI-Driven Chatbot**: 사용자의 입력에 따라 AI가 실시간으로 텍스트를 생성합니다.
- **Google Docs Integration**: 생성된 텍스트를 Google Docs에 바로 반영영 가능.
- **Responsive Design**: 반응형 디자인으로 다양한 화면 크기에서도 완벽히 작동.
- **Authentication**: Google 로그인 기능 제공.
- **User-Friendly Interface**: 간결하고 직관적인 Sideabr UI.

---

## 🗂 File Structure

```
frontend/
├── icon_circle.png           # 아이콘 파일
├── manifest.json             # Chrome Extension 설정 파일
├── sidebar.html              # 사이드 패널 HTML
├── sidebar.js                # 사이드 패널 JS (주요 기능 구현)
├── style.css                 # 사이드 패널 스타일
├── login_2.html              # 로그인 페이지 HTML
├── login_2.css               # 로그인 페이지 스타일
├── start.html                # 시작 페이지 HTML
├── start.css                 # 시작 페이지 스타일
└── README.md                 # 프로젝트 설명
```

---

## 🛠 Tech Stack

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Google Docs API](https://img.shields.io/badge/Google%20Docs%20API-4285F4?style=for-the-badge&logo=google&logoColor=white)
![OpenAI GPT API](https://img.shields.io/badge/OpenAI%20API-412991?style=for-the-badge&logo=openai&logoColor=white)
![Chrome Extensions](https://img.shields.io/badge/Chrome%20Extensions-4285F4?style=for-the-badge&logo=googlechrome&logoColor=white)

---

## ⚙️ Setup and Installation

### Prerequisites
- Chrome 브라우저

### Installation Steps
1. **Repository Clone**
   ```bash
   git clone -b frontend https://github.com/your-repo/finpilot.git
   cd finpilot/frontend
   ```

2. **Chrome Extension 설치**
   - Chrome의 `chrome://extensions`로 이동.
   - "Developer mode"를 활성화한 뒤 "Load unpacked"를 클릭.
   - `frontend` 폴더를 선택하여 확장 프로그램을 로드합니다.

---

## 🚀 How to Run

1. **Extension 실행**:
   - Chrome에서 FinPilot 확장 아이콘을 우클릭.
   - 측면 패널 열기 클릭
   - Google Docs 페이지에서 동작 확인.

2. **AI 기능 테스트**:
   - SidePanel에서 질문을 입력하거나 문장을 생성.
   - 생성된 텍스트가 Google Docs에 자동으로 반영되는지 확인.

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

- **Email**: sjh75555@naver.com
- **GitHub**: [https://github.com/wkd-gh](https://github.com/wkd-gh)

---

> 이 README는 **FinPilot 프론트엔드 브랜치**에 최적화된 문서입니다. 
> 전체 프로젝트에 대한 자세한 내용은 Main 브랜치의 README를 참조하세요.