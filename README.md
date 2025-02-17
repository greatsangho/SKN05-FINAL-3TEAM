<p align="center">
  <img src="https://github.com/user-attachments/assets/2ededb0c-b0e1-4248-acf7-3829b37de094" style="width:100%;" alt="Strapi logo" />
</p>

## **FinPilot: AI 기반 비즈니스 문서 작성 어시스턴트**  
> 비즈니스 문서 작성을 쉽고 효율적으로 도와주는 스마트 가이드!

`FinPilot` 프로젝트에 오신 것을 환영합니다! 
이 프로젝트는 Google Docs 환경에서 사용자가 더 효율적으로 문서를 작성하고 관리할 수 있도록 설계된 AI 어시스턴트 서비스를 개발하는 것을 목표로 시작되었습니다. `Chrome Extension`과 `LangGraph` 기반의 LLM 애플리케이션인 `FinPilot`을 통합하여 문서 초안 생성, 단락 작성, 데이터 분석/시각화 등의 기능을 제공합니다.

[![Web Store](https://img.shields.io/badge/Chrome%20Web%20Store-v.1.0.6-blue)](https://chromewebstore.google.com/detail/finpilot/hpdfbpijlbahkobocmggbdlbajicbkda?hl=ko&utm_source=ext_sidebar) 
[![YouTube](https://img.shields.io/badge/YouTube-Introduce-red)](https://www.youtube.com/watch?v=QYsDuSCmkFs)
[![Notion](https://img.shields.io/badge/Notion-FinPilot%20Home-lightgrey)](https://alluring-cerise-57f.notion.site/FinPilot-Home-1655128db47f80cabc52e0568a116d94)
[![최종 발표 자료](https://img.shields.io/badge/Presentation-최종발표-orange)](https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN05-FINAL-3TEAM/blob/main/Docs/SKN05_3Team_%EC%B5%9C%EC%A2%85%EB%B0%9C%ED%91%9C%EC%9E%90%EB%A3%8C.pdf)

## Features
- **AI-Driven Chatbot** : 
    - AI 기반 비즈니스 문서 작성 및 보완 지원
    - 채팅 중 파일 첨부 지원
    - 답변을 조정할 수 있는 5가지 옵션 제공
- **Google Docs Integration** :
    - Google Docs와의 원활한 통합, 생성된 텍스트를 Google Docs에 바로 반영 가능.
- **Responsive Design** :
    - 반응형 디자인으로 다양한 화면 크기에서도 완벽히 작동.
- **Authentication** :
    - Google 로그인 기능 제공.
- **User-Friendly Interface** :
    - AI 인터랙션을 위한 간결하고 직관적인 Sidebar UI.

## Tech Stack
- **Chrome Extension** : 
    HTML, CSS, JavaScript
- **Server** : 
    OpenAI API
- **LLM Application** : 
    Manifest v3

---

## 📌 Table of Content
1. [FinPilot 개요](#finpilot-개요)
2. [실행 예시](#실행-예시)
3. [주요 기능](#주요-기능)
4. [필수 조건](#필수-조건)
5. [시작하기](#시작하기)
6. [파일 구조](#파일-구조)
7. [기여자](#기여자)
8. [커뮤니케이션](#커뮤니케이션)

---

## 🔍 About FinPilot
FinPilot은 AI를 활용하여 금융 문서 작성을 지원하는 Chrome 확장 프로그램입니다. Google Docs 내에서 AI가 제공하는 문서 작성 및 개선 기능을 사이드바를 통해 손쉽게 활용할 수 있습니다.

## 🎬 실행 예시
![FinPilot 데모](./assets/finpilot_demo.gif)

## 🚀 주요 기능
### 🏗 애플리케이션 구조


## 🛠 Requirements
- Google Chrome
- OpenAI API 키
- Google OAuth 2.0 인증 정보

## ⚡How to Get Start in Local
### Chrome 확장 프로그램 테스트
1. 이 저장소를 다운로드하거나 클론합니다.
2. Chrome에서 `chrome://extensions/` 페이지를 엽니다.
3. **개발자 모드**를 활성화합니다.
4. **압축 해제된 확장 프로그램 로드** 버튼을 클릭하고 `FinPilot` 폴더를 선택합니다.
5. 확장 프로그램을 고정하여 사용을 시작합니다!

### FinPilot API 테스트
1. OpenAI API 키를 발급받습니다.
2. `src/sidebar.js` 파일에 API 키를 입력합니다.
3. 확장 프로그램을 다시 로드한 후 AI 기능을 테스트합니다.

## 📂 파일 구조
```
FinPilot/
├── src/
│   ├── background.js
│   ├── content.js
│   ├── popup.js
│   ├── sidebar.js
│   ├── styles.css
│   ├── manifest.json
└── assets/
```

## 👥 Contributors
| 이름       | GitHub | Gmail | Instagram |
|------------|--------|--------|------------|
| 서장호 | [GitHub](https://github.com/jangho-seo) | jangho@gmail.com | [@jangho_fin](https://instagram.com/jangho_fin) |
| 팀원 2 | [GitHub](https://github.com/member2) | member2@gmail.com | [@member2](https://instagram.com/member2) |
| 팀원 3 | [GitHub](https://github.com/member3) | member3@gmail.com | [@member3](https://instagram.com/member3) |
| 팀원 4 | [GitHub](https://github.com/member4) | member4@gmail.com | [@member4](https://instagram.com/member4) |

## 📢 Communication
[![Discord](https://img.shields.io/badge/Discord-참여하기-blue)](https://slack.com/FinPilot)
[![Notion](https://img.shields.io/badge/Notion-프로젝트%20문서-lightgrey)](https://notion.so/FinPilot)

## Contact
문의 사항이 있으면 Slack 또는 이메일을 통해 연락 주세요!