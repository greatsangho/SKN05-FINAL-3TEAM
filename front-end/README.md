# 🚀 FinPilot - Frontend

FinPilot은 Google Docs와 원활하게 통합된 sLLM 기반 Chrome Extension입니다. 

**Frontend**는 사용자가 직관적으로 접근할 수 있는 사용자 인터페이스를 제공하며, sLLM을 활용하여 금융 문서 생성 및 편집을 돕습니다.

---

## 📖 Table of Contents
- [About the Project](#-about-the-project)
- [Features](#-features)
- [File Structure](#-file-structure)
- [Tech Stack](#-tech-stack)
- [Communication](#-communication)
- [Setup and Installation](#-setup-and-installation)
- [How to Run](#-how-to-run)
- [Contribution](#-contribution)
- [Contact](#-contact)

---

## 📋 About the Project

FinPilot은 Google Docs 환경에서 사용자가 더 효율적으로 금융 문서를 작성하고 관리할 수 있도록 설계된 **Chrome Extension**입니다. 
이 프로젝트는 **sLLM 기반 텍스트 생성**과 **Google Docs 연동**을 핵심 기능으로 제공합니다.

---

## ✨ Features

- **AI-Driven Chatbot**: 사용자의 입력에 따라 AI가 실시간으로 텍스트를 생성.
- **Google Docs Integration**: 생성된 텍스트를 Google Docs에 바로 반영 가능.
- **Responsive Design**: 반응형 디자인으로 다양한 화면 크기에서도 완벽히 작동.
- **Authentication**: Google 로그인 기능 제공.
- **User-Friendly Interface**: 간결하고 직관적인 Sidebar UI.

---

## 🗂 File Structure

```
front-end/
├── README.md                  # 프로젝트 설명
├── chrome_extension/          # Chrome 확장 프로그램 폴더
│   ├── .gitignore              # Git 설정 파일
│   ├── apply.png               # apply 버튼 아이콘
│   ├── background.js           # background 스크립트
│   ├── chat_option.png         # 채팅 옵션 버튼 아이콘
│   ├── check-icon.png          # 체크 아이콘
│   ├── copy.png                # 복사 버튼 아이콘
│   ├── copy_done.png           # 복사 완료 아이콘
│   ├── default_profile.webp    # 기본 프로필 이미지
│   ├── file_upload.png         # 파일 업로드 버튼 아이콘
│   ├── guide.gif               # 팝업창 가이드 GIF
│   ├── icon_16.png             # FinPilot 로고 (16px)
│   ├── icon_32.png             # FinPilot 로고 (32px)
│   ├── icon_48.png             # FinPilot 로고 (48px)
│   ├── icon_64.png             # FinPilot 로고 (64px)
│   ├── icon_128.png            # FinPilot 로고 (128px)
│   ├── icon_circle.png         # FinPilot 원형 로고
│   ├── manifest.json           # Chrome Extension 설정 파일
│   ├── package-lock.json       # 패키지 종속성 파일
│   ├── package.json            # 패키지 설정 파일
│   ├── popup.css               # 팝업창 스타일
│   ├── popup.html              # 팝업창 페이지
│   ├── popup.js                # 팝업창 스크립트
│   ├── privacy-policy.md       # FinPilot 개인정보 보호 정책
│   ├── send_icon.png           # 전송 버튼 아이콘
│   ├── sidebar.html            # 사이드바 HTML
│   ├── sidebar.js              # 사이드바 기능 구현
│   ├── sidebar_cursor.js       # 사이드바 커서 기능
│   ├── sidebar_serviceaccount.js # 사이드바 서비스 계정 구현
│   ├── style.css               # 사이드바 스타일 시트
│   ├── web/                    # 웹페이지 관련 폴더
│   │   ├── info/               # 채팅 옵션 info 페이지 관련 폴더
│   │   │   ├── info.css        # 채팅 옵션 info 스타일
│   │   │   ├── info.html       # 채팅 옵션 info HTML
│   │   ├── landing/            # 랜딩 페이지 관련 폴더 
│   │   │   ├── landing.html    # 랜딩 페이지 HTML
│   │   │   ├── landing_files/  # 랜딩 페이지 이미지 및 리소스
│   │   │   │   ├── background.png
│   │   │   │   ├── fp_gif_1.gif
│   │   │   │   ├── fp_gif_2.gif
│   │   │   │   ├── fp_png_1.png
│   │   │   │   ├── fp_png_2.png
│   │   │   │   ├── script
│   │   │   │   ├── script_main.Y4SCJLDF.mjs
│   │   ├── login/              # 로그인 페이지 관련 폴더
│   │   │   ├── login.css       # 로그인 페이지 스타일
│   │   │   ├── login.html      # 로그인 페이지 HTML
│   │   │   ├── login.js        # 로그인 페이지 스크립트
│   │   ├── start/              # 시작 페이지 관련 폴더더
│   │   │   ├── start.css       # 시작 페이지 스타일
│   │   │   ├── start.html      # 시작 페이지 HTML
│   │   │   ├── start.js        # 시작 페이지 스크립트
```

---

## 🛠 Tech Stack

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Google Drive API](https://img.shields.io/badge/Google%20Drive%20API-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)
![Google Docs API](https://img.shields.io/badge/Google%20Docs%20API-4285F4?style=for-the-badge&logo=google&logoColor=white)
![OpenAI GPT API](https://img.shields.io/badge/OpenAI%20API-412991?style=for-the-badge&logo=openai&logoColor=white)
![Chrome Extensions](https://img.shields.io/badge/Chrome%20Extensions-4285F4?style=for-the-badge&logo=googlechrome&logoColor=white)
![Figma](https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white)
![Framer](https://img.shields.io/badge/Framer-0055FF?style=for-the-badge&logo=framer&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)


---

## 📢 Communication

![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white)

---

## ⚙️ Setup and Installation

### Prerequisites
- Chrome 브라우저
- Google Account
- Google Docs

### Installation Steps
1. **Repository Clone**
   ```bash
   git clone -b frontend https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN05-FINAL-3TEAM.git
   cd main/front-end
   ```

2. **Chrome Extension 로드**
   - Chrome의 `chrome://extensions`로 이동.
   - "Developer mode"를 활성화한 뒤 "Load unpacked"를 클릭.
   - `chrome_extension` 폴더를 선택하여 확장 프로그램을 로드합니다.

---

## 🚀 How to Run

1. **Extension 실행**:
   - Google Docs 페이지에서 문서 열기.
   - Chrome 브라우저에서 우측 상단 FinPilot 확장 아이콘 우클릭.
   - 측면 패널 열기 선택

2. **AI 기능 테스트**:
   - SidePanel에서 원하는 채팅 옵션 선택 후, 질문 입력.
   - 생성된 텍스트 확인
   - apply 버튼으로 생성 텍스트가 Google Docs 문서에 자동으로 반영되는지 확인

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