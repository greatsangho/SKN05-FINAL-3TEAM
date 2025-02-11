// 문서 아이디 초기값 설정
let DOCUMENT_ID = ""; 

// 현재 활성탭을 가져와 문서 id 찾기
function getDocumentIdFromActiveTab() {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, lastFocusedWindow: true }, (tabs) => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError.message);
        return;
      }

      if (!tabs.length || !tabs[0].url) {
        reject("활성 탭을 찾을 수 없습니다.");
        return;
      }

      const url = tabs[0].url;
      console.log("현재 탭 URL:", url);

      if (!url.includes("https://docs.google.com/document/")) {
        reject("Google Docs 문서 페이지가 아닙니다.");
        return;
      }

      const match = url.match(/\/d\/([a-zA-Z0-9_-]+)/); // 문서 ID 추출
      if (match) {
        resolve(match[1]);
      } else {
        reject("URL에서 Google Docs 문서 ID를 찾을 수 없습니다.");
      }
    });
  });
}

let globalUserEmail = "";  // 유저 이메일을 전역 변수로 선언
// 찾은 문서 아이디와 사용자 이메일 FastAPI 서버로 전송
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const docId = await getDocumentIdFromActiveTab();
    if (docId) {
      DOCUMENT_ID = docId;
      console.log(`문서 ID 자동 추출 성공: ${DOCUMENT_ID}`);
      console.log(`Google Docs 문서가 연동되었습니다.\n\n문서 ID: ${DOCUMENT_ID}`);

      // Google 사용자 이메일 가져오기
      chrome.identity.getAuthToken({ interactive: true }, async (token) => {
        if (chrome.runtime.lastError) {
          console.error('Google 로그인 실패:', chrome.runtime.lastError);
          alert("Google 로그인에 실패했습니다. 다시 시도해주세요.");
          return;
        }

        // 버퍼링 시작
        showLoadingSpinner();

        try {
          // 사용자 정보 가져오기
          const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
            headers: { Authorization: `Bearer ${token}` },
          });

          const userData = await response.json();
          if (userData.email) {
            console.log(`사용자 이메일 가져오기 성공: ${userData.email}`);
            globalUserEmail = userData.email;  // 전역 변수에 이메일 저장

            // FastAPI 서버로 전송할 데이터
            const requestData = {
              docs_id: DOCUMENT_ID,   // 문서 ID
              user_email: userData.email  // 사용자 이메일
            };

            // FastAPI 서버로 POST 요청
            fetch('https://finpilotback.duckdns.org/sessions/', { 
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
              },
              body: JSON.stringify(requestData),
            })
            .then((res) => res.json())
            .then((data) => {
              console.log("서버 응답:", data);
              //alert("서버와 성공적으로 연결되었습니다!"); // 서버와 정상적으로 세션 연결
            })
            .catch((error) => {
              console.error("서버 전송 실패:", error);
              alert("서버 연결 중 오류가 발생했습니다.");
            });

          } else {
            console.error("이메일 정보를 가져오지 못했습니다.");
            alert("Google 계정 정보를 가져올 수 없습니다.");
          }
        } catch (error) {
          console.error("사용자 정보 가져오기 실패:", error);
          alert("사용자 정보를 불러오는 중 오류가 발생했습니다.");
        } finally{
          hideLoadingSpinner();
        }
      });
    }
  } catch (error) {
    // console.error("문서 ID 추출 실패:", error);
    alert("현재 활성 탭은 Google Docs 문서 페이지가 아닙니다.\nGoogle Docs 문서를 열고 다시 시도해주세요.\n\n - 예시 URL: https://docs.google.com/document/d/문서ID/edit");
  }
});

// 로딩 버퍼링 스피너 제어 함수
function showLoadingSpinner() {
  const spinner = document.getElementById("loading-spinner");
  const chatContainer = document.querySelector(".chat-container");
  if (spinner) spinner.style.display = "block";
  if (chatContainer) chatContainer.classList.add("loading"); // 흐림 효과 추가
}
function hideLoadingSpinner() {
  const spinner = document.getElementById("loading-spinner");
  const chatContainer = document.querySelector(".chat-container");
  if (spinner) spinner.style.display = "none";
  if (chatContainer) chatContainer.classList.remove("loading"); // 흐림 효과 제거
}

// --------------------------------------------------------
// 🚀 1️⃣ 로딩 UI 표시 함수 (화면 흐려짐 + 중앙에 로딩 UI 표시 -> 프로그레스 바 + 금융 명언/퀴즈)
// --------------------------------------------------------
function showLoadingUI() {
  const loadingContainer = document.getElementById("loading-container");
  const chatContainer = document.querySelector(".chat-container");

  if (!loadingContainer || !chatContainer) {
      console.error("❌ ERROR: loading-container 또는 chat-container를 찾을 수 없음.");
      return;
  }

  console.log("✅ showLoadingUI 실행됨!");

  // 화면 흐려지게 만들기
  chatContainer.classList.add("loading");

  // 로딩 UI 표시
  loadingContainer.style.display = "flex";
  loadingContainer.style.justifyContent = "center";
  loadingContainer.style.alignItems = "center";
  loadingContainer.style.position = "absolute";
  loadingContainer.style.top = "50%";
  loadingContainer.style.left = "50%";
  loadingContainer.style.transform = "translate(-50%, -50%)";
  loadingContainer.style.background = "rgba(255, 255, 255, 0.9)";
  loadingContainer.style.padding = "20px";
  loadingContainer.style.borderRadius = "10px";
  loadingContainer.style.boxShadow = "0px 4px 10px rgba(0, 0, 0, 0.1)";

  startLoadingAnimation(currentSelectedOption);
  displayRandomFinanceTip();  // 랜덤 금융 명언 표시
  loadRandomQuiz();  // 금융 퀴즈 로드
}

let progressInterval = null;
// ⏳ 2️⃣ 프로그레스 바 업데이트
function startLoadingAnimation(currentSelectedOption) {
    const progressBar = document.getElementById("progress-bar");
    const loadingMessage = document.getElementById("loading-message");
    const spinner = document.getElementById("loading-spinner_");

    if (!progressBar || !loadingMessage) {
        console.error("❌ ERROR: progressBar 또는 loadingMessage 요소를 찾을 수 없음.");
        return;
    }

    console.log("✅ startLoadingAnimation 실행됨!");

    // ✅ 기존 인터벌 제거 (중복 실행 방지)
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }

    let maxTime, minTime;
    if (currentSelectedOption === "초안 작성") {
        maxTime = 60000 * 5; // 5분
        minTime = 2000; // 2초
    } else if (currentSelectedOption === "단락 생성") {
        maxTime = 30000; // 30초
        minTime = 2000; // 2초
    } else if (currentSelectedOption === "요약 / 확장") {
        maxTime = 5000; // 5초
        minTime = 2000; // 2초
    } else if (currentSelectedOption === "데이터 시각화 (Web)") {
        maxTime = 60000 * 2; // 2분 
        minTime = 2000; // 2초
    } else {
        maxTime = 60000 * 2; // 2분
        minTime = 2000; // 2초
    }

    const startTime = Date.now();
    let isResponseReceived = false; // 응답 도착 상태 초기화
    let estimatedProgress = 1; // ✅ 진행률 초기화

    // ✅ 첫 시작 시 진행 바 초기화
    progressBar.style.width = "1%";
    loadingMessage.textContent = `FinPilot이 답변을 준비하는 중.. 1%`;
    spinner.style.display = "inline-block";

    // ✅ `maxTime`에 정확히 맞춰 업데이트 주기 계산 (최소 100ms 보장)
    let updateInterval = Math.max(maxTime / 100, 100);
    let totalSteps = Math.ceil(maxTime / updateInterval); // 총 업데이트 횟수
    let progressStep = 99 / totalSteps; // 한 번 실행할 때 증가할 진행률

    console.log(`🔄 진행 바 업데이트 주기: ${updateInterval}ms, 총 업데이트 횟수: ${totalSteps}, 1회 증가량: ${progressStep}%`);

    function updateProgress() {
        if (isResponseReceived) return;

        const elapsedTime = Date.now() - startTime;
        estimatedProgress = Math.min(progressStep * (elapsedTime / updateInterval), 99);

        if (estimatedProgress <= parseFloat(progressBar.style.width)) return;

        progressBar.style.width = estimatedProgress + "%";
        loadingMessage.textContent = `FinPilot이 답변을 준비하는 중.. ${Math.floor(estimatedProgress)}%`;
        console.log(`🟢 진행률 업데이트: ${Math.floor(estimatedProgress)}%`);

        if (elapsedTime >= maxTime) {
            console.log("🚨 서버 응답이 늦음! 프로그레스 바 100% 유지 중...");
            clearInterval(progressInterval);
            progressInterval = null;
        }
    }

    // ✅ 새로운 업데이트 인터벌 시작 전에 기존 인터벌을 제거
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    progressInterval = setInterval(updateProgress, updateInterval);

    function completeProgress() {
        if (isResponseReceived) return;
        isResponseReceived = true;

        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }

        const remainingTime = Math.max(minTime - (Date.now() - startTime), 0);
        setTimeout(() => {              
            progressBar.style.width = "100%";
            loadingMessage.textContent = "FinPilot이 마지막 점검을 마치는 중입니다.";
            spinner.style.display = "none";
            console.log("✅ 프로그레스 바 100% 도달!");

            estimatedProgress = 1;
        }, remainingTime);
    }

    return completeProgress;
}

// 🎯 3️⃣ 로딩 완료 후 UI 숨기기 (화면 흐림 제거 + 로딩 UI 숨김)
function hideLoadingUI() {
  const loadingContainer = document.getElementById("loading-container");
  const chatContainer = document.querySelector(".chat-container");

  if (!loadingContainer || !chatContainer) {
      console.error("❌ ERROR: loading-container 또는 chat-container를 찾을 수 없음.");
      return;
  }

  console.log("✅ hideLoadingUI 실행됨!");

  // 화면 흐림 제거
  chatContainer.classList.remove("loading");

  // 로딩 UI 숨기기
  loadingContainer.style.display = "none";
}

// 💡 4️⃣ 랜덤 금융 명언/팁 제공
function displayRandomFinanceTip() {
  const financeTips = [
    `<img src="Advice.png" alt="투자" style="width:16px; height:16px;"> 워렌 버핏: 좋은 투자란 기다림의 미학이다.`,
    `<img src="Advice.png" alt="감정 통제" style="width:16px; height:16px;"> 벤저민 그레이엄: 현명한 투자자는 감정을 통제할 줄 알아야 한다.`,
    `<img src="Advice.png" alt="기업 투자" style="width:16px; height:16px;"> 피터 린치: 당신이 이해하는 기업에 투자하라.`,
    `<img src="Advice.png" alt="장기 투자" style="width:16px; height:16px;"> 존 보글: 장기적인 인내심이 가장 중요한 투자 전략이다.`,
    `<img src="Advice.png" alt="복리" style="width:16px; height:16px;"> 찰리 멍거: 단순한 원칙을 따르면서 복리의 힘을 활용하라.`,
    `<img src="Advice.png" alt="기회" style="width:16px; height:16px;"> 조지 소로스: 시장은 항상 틀릴 수 있다. 기회를 찾아라.`,
    `<img src="Advice.png" alt="매수 기회" style="width:16px; height:16px;"> 존 템플턴: 가장 비관적인 시점에서 주식을 사라.`,
    `<img src="Advice.png" alt="위험 관리" style="width:16px; height:16px;"> 하워드 막스: 위험을 낮추는 것은 수익을 희생하는 것이 아니다.`,
    `<img src="Advice.png" alt="감정 통제" style="width:16px; height:16px;"> 제시 리버모어: 시장에서 가장 큰 위험은 당신 자신의 감정이다.`,
    `<img src="Advice.png" alt="리스크 관리" style="width:16px; height:16px;"> 레이 달리오: 모든 투자는 리스크 관리가 핵심이다.`,
    `<img src="diversified_investment.png" alt="분산 투자" style="width:16px; height:16px;"> 분산 투자: 하나의 자산에 집중하기보다 다양한 자산에 투자하세요.`,
    `<img src="up_graph.png" alt="장기 투자" style="width:16px; height:16px;"> 장기 투자: 단기 변동성을 신경 쓰지 말고 장기적인 성장에 집중하세요.`,
    `<img src="down_graph.png" alt="손절매" style="width:16px; height:16px;"> 손절매 전략: 손실을 감당할 수 있는 선에서 미리 정해두세요.`,
    `<img src="Analysis.png" alt="기업 분석" style="width:16px; height:16px;"> 기업 분석: 재무제표를 확인하고 회사의 기본적인 가치를 분석하세요.`,
    `<img src="credit.png" alt="신용 관리" style="width:16px; height:16px;"> 신용 관리: 높은 이자를 부담하는 부채를 먼저 갚는 것이 중요합니다.`,
    `<img src="sad.png" alt="감정적 투자 금지" style="width:16px; height:16px;"> 감정적 투자 금지: 공포와 탐욕을 통제하고 감정적 결정을 피하세요.`,
    `<img src="money_hand.png" alt="배당 투자" style="width:16px; height:16px;"> 배당 투자: 꾸준한 배당을 지급하는 기업을 찾아보세요.`,
    `<img src="money.png" alt="시장 조사" style="width:16px; height:16px;"> 시장 조사: 트렌드와 경제 흐름을 꾸준히 파악하세요.`,
    `<img src="rebalancing.png" alt="리밸런싱" style="width:16px; height:16px;"> 리밸런싱: 포트폴리오를 정기적으로 점검하고 조정하세요.`
  ];

  const randomTip = financeTips[Math.floor(Math.random() * financeTips.length)];
  document.getElementById("finance-tip").innerHTML = randomTip;

}

// 🎯 5️⃣ 금융 퀴즈 제공
function loadRandomQuiz() {
  const quizData = [
    {
        question: "ETF와 뮤추얼펀드의 차이는?",
        options: ["액티브 vs 패시브 관리", "둘 다 동일", "ETF는 펀드가 아니다"],
        correct: 0
    },
    {
        question: "다음 중 금융 시장에서 '베어마켓'이 의미하는 것은?",
        options: ["시장 상승", "시장 하락", "시장 변동 없음"],
        correct: 1
    },
    {
        question: "다음 중 '주식 분할(Stock Split)'의 효과는?",
        options: ["주가 상승", "유통 주식 수 증가", "배당 수익 증가"],
        correct: 1
    },
    {
        question: "다음 중 인플레이션(Inflation)의 정의는?",
        options: ["물가가 지속적으로 하락하는 현상", "화폐 가치가 상승하는 현상", "물가가 지속적으로 상승하는 현상"],
        correct: 2
    },
    {
        question: "다음 중 '배당 수익률'을 계산하는 방법은?",
        options: ["배당금 ÷ 주가 × 100", "주가 ÷ 배당금 × 100", "순이익 ÷ 배당금 × 100"],
        correct: 0
    },
    {
        question: "다음 중 '채권(Bond)'의 특징이 아닌 것은?",
        options: ["고정적인 이자를 지급한다", "정부나 기업이 발행할 수 있다", "주식보다 변동성이 크다"],
        correct: 2
    },
    {
        question: "다음 중 '리스크 분산'을 위해 가장 적절한 전략은?",
        options: ["한 종목에 집중 투자", "다양한 자산에 투자", "빚을 내서 투자"],
        correct: 1
    },
    {
        question: "기업의 'PER(주가수익비율)'이 의미하는 것은?",
        options: ["주가 ÷ 주당순이익", "배당금 ÷ 주가", "자산 ÷ 부채"],
        correct: 0
    },
    {
        question: "다음 중 중앙은행이 금리를 인상하면 일반적으로 발생하는 효과는?",
        options: ["대출 금리가 낮아진다", "주식 시장이 상승한다", "경제 성장이 둔화될 가능성이 높다"],
        correct: 2
    },
    {
        question: "다음 중 '기본적 분석(Fundamental Analysis)'의 주요 요소가 아닌 것은?",
        options: ["기업의 재무제표 분석", "기술적 차트 분석", "산업 및 거시경제 분석"],
        correct: 1
    },
    {
        question: "다음 중 '주가가 하락할 때 수익을 내는 투자 전략'은?",
        options: ["공매도", "배당 투자", "인덱스 펀드 투자"],
        correct: 0
    },
    {
        question: "다음 중 'S&P 500'이 의미하는 것은?",
        options: ["세계 500대 기업", "미국 대형주 500개 지수", "미국 500개 은행"],
        correct: 1
    },
    {
        question: "다음 중 경제 성장과 가장 밀접한 지표는?",
        options: ["GDP(국내총생산)", "PER(주가수익비율)", "CPI(소비자물가지수)"],
        correct: 0
    },
    {
        question: "다음 중 '달러 강세'가 미치는 영향으로 옳은 것은?",
        options: ["수출 기업에 유리하다", "원유 가격이 상승한다", "달러 환율이 상승한다"],
        correct: 2
    },
    {
        question: "다음 중 '하이일드 채권(High-Yield Bond)'의 특징은?",
        options: ["신용 등급이 높다", "이자율이 높다", "변동성이 낮다"],
        correct: 1
    }
  ];
  const randomQuiz = quizData[Math.floor(Math.random() * quizData.length)];
  document.getElementById("quiz-question").textContent = randomQuiz.question;
  
  const options = document.querySelectorAll(".quiz-option");
  options.forEach((button, index) => {
      button.textContent = randomQuiz.options[index];
      button.onclick = () => {
          if (index === randomQuiz.correct) {
              alert("🎯 정답입니다!");

              // 🚀 정답을 맞췄으므로 새로운 퀴즈 & 명언/팁 불러오기
              displayRandomFinanceTip(); // 새로운 금융 명언/팁 로드
              loadRandomQuiz(); // 새로운 금융 퀴즈 로드
              
          } else {
              alert("⚠ 오답입니다! 다시 시도해보세요.");
          }
      };
  });
}

// ------------------------
// "Send" 버튼 클릭 이벤트
// ------------------------
document.getElementById("send-btn").addEventListener("click", async () => {
    const userInput = document.getElementById("user-input").value.trim();
    if (!userInput) {
        alert("질문 입력 후 시도해주세요.");
        return;
    }

    const greetingElement = document.getElementById('greeting');
    if (greetingElement) {
        greetingElement.style.display = 'none';
    }

    const chatBox = document.getElementById("chat-box");

    // 사용자가 입력한 텍스트에서 줄바꿈 처리
    const formattedMessage = userInput.replace(/\n/g, "<br>");

    // 사용자 메시지 추가
    const userMessage = document.createElement("div");
    userMessage.classList.add("chat-message", "question");
    userMessage.innerHTML = formattedMessage;  // 줄바꿈을 적용한 HTML 추가
    chatBox.appendChild(userMessage);

    // 로딩 스피너 표시
    // showLoadingSpinner();
    showLoadingUI(); // 🚀 로딩 UI 실행
    const completeProgress = startLoadingAnimation(currentSelectedOption); // 🚀 프로그레스 바 시작

    try {
        const requestData = {
            user_email: globalUserEmail,
            docs_id: DOCUMENT_ID,
            question: userInput,
            chat_option: currentSelectedOption
        };

        const response = await fetch("https://finpilotback.duckdns.org/qnas/", {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "질문 전송 실패");
        }

        const result = await response.json();

        // FastAPI 응답 메시지 생성
        const botMessageElement = document.createElement("div");
        botMessageElement.classList.add("chat-message", "answer");

        if (currentSelectedOption === "데이터 시각화 (Web)" || currentSelectedOption === "데이터 시각화 (Upload)") {
            if (result.images && result.images.length > 0) {
              result.images.forEach((image, index) => {
                  // 이미지 컨테이너 생성
                  const imageContainer = document.createElement("div");
                  imageContainer.classList.add("image-container");
                  imageContainer.style.position = "relative";  // 상대 위치 설정
                  imageContainer.style.display = "inline-block";
                  imageContainer.style.border = "1px solid #ccc";
                  imageContainer.style.borderRadius = "10px";
                  imageContainer.style.padding = "10px";
                  imageContainer.style.marginBottom = "20px";
                  imageContainer.style.textAlign = "center";

                  // 좌측 상단 FinPilot 아이콘 (항상 보이도록 설정)
                  const leftIcon = document.createElement("img");
                  leftIcon.src = "icon_circle.png";
                  leftIcon.alt = "FinPilot Icon";
                  leftIcon.style.position = "absolute";
                  leftIcon.style.top = "10px";
                  leftIcon.style.left = "10px";
                  leftIcon.style.width = "32px";
                  leftIcon.style.height = "32px";
                  leftIcon.style.zIndex = "1";

                  // 현재 시간 포맷팅 함수
                  function getFormattedTime() {
                    const now = new Date();
                    return now.toLocaleString("ko-KR", { 
                        year: "numeric", 
                        month: "2-digit", 
                        day: "2-digit", 
                        hour: "2-digit", 
                        minute: "2-digit", 
                        second: "2-digit" 
                    });
                  }

                  // 우측 하단 시간 표시 요소 추가
                  const timestamp = document.createElement("small");
                  timestamp.textContent = getFormattedTime();
                  timestamp.style.position = "absolute";
                  timestamp.style.bottom = "5px";
                  timestamp.style.right = "10px";
                  timestamp.style.color = "#888";
                  timestamp.style.fontSize = "11.8px";

                  // 버튼 컨테이너 (기본적으로 숨김)
                  const buttonContainer = document.createElement("div");
                  buttonContainer.classList.add("image-buttons");
                  buttonContainer.style.position = "absolute";
                  buttonContainer.style.top = "10px";
                  buttonContainer.style.right = "10px";
                  buttonContainer.style.opacity = "0";  // 기본적으로 숨김
                  buttonContainer.style.transition = "opacity 0.15s ease-in-out";
                  buttonContainer.style.zIndex = "1";

                  // 이미지 hover 시 버튼 표시
                  imageContainer.addEventListener("mouseenter", () => {
                    buttonContainer.style.opacity = "1"; // 보이기
                  });
                  imageContainer.addEventListener("mouseleave", () => {
                      buttonContainer.style.opacity = "0"; // 숨기기
                  });

                  // 버튼 스타일 제거 (테두리 및 배경)
                  const styleButtons = (button) => {
                    button.style.border = "none";  // 테두리 제거
                    button.style.outline = "none"; // 포커스 테두리 제거
                    button.style.background = "none";  // 배경 제거
                    button.style.cursor = "pointer";   // 마우스 오버 시 커서 변경
                    button.style.padding = "5px";      // 간격 조정
                  };

                  // 스타일 추가 (툴팁을 위한 CSS 추가)
                  const style = document.createElement("style");
                  style.innerHTML = `
                    .tooltip-container {
                      position: relative;
                      display: inline-block;
                    }
                    .tooltip-container .tooltip-text {
                      visibility: hidden;
                      width: auto;
                      background-color: #333;
                      color: #fff;
                      text-align: center;
                      border-radius: 5px;
                      padding: 5px 8px;
                      position: absolute;
                      z-index: 20;
                      top: -26px;
                      right: 50%;
                      transform: translateX(50%);
                      font-size: 10px;
                      white-space: nowrap;
                      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                      opacity: 0;
                      transition: opacity 0.15s ease-in-out, visibility 0.15s ease-in-out;
                    }
                    .tooltip-container .tooltip-text::after {
                      content: "";
                      position: absolute;
                      top: 100%;  /* 말풍선 아래쪽에 위치 */
                      left: 50%;
                      transform: translateX(-50%);
                      border-width: 4px;
                      border-style: solid;
                      border-color: #333 transparent transparent transparent;
                    }
                    .tooltip-container:hover .tooltip-text {
                      visibility: visible;
                      opacity: 1;
                    }
                  `;
                  document.head.appendChild(style);
      
                  // Apply 버튼 추가
                  const applyButton = document.createElement("button");
                  applyButton.classList.add("apply-btn", "tooltip-container");
                  applyButton.innerHTML = `
                      <img src="./apply.png" alt="Apply" style="width: 16px; height: 16px;">
                      <span class="tooltip-text">Apply to Docs</span>
                  `;
      
                  // Copy 버튼 추가
                  const copyButton = document.createElement("button");
                  copyButton.classList.add("copy-btn", "tooltip-container");
                  copyButton.innerHTML = `
                      <img src="./copy.png" alt="Copy" style="width: 16px; height: 16px;">
                      <span class="tooltip-text">Copy</span>
                  `;

                  // source 버튼 추가
                  const sourceButton = document.createElement("button");
                  sourceButton.classList.add("source-btn", "tooltip-container");
                  sourceButton.innerHTML = `
                      <img src="./source.png" alt="Source" style="width: 16px; height: 16px;">
                      <span class="tooltip-text">Source</span>
                  `;
      
                  // Apply 버튼 클릭 기능 (이미지 삽입)
                  applyButton.addEventListener("click", () => {
                      appendImageToGoogleDoc(image.image_data, "image/png");
                      const imgElement = applyButton.querySelector("img");
                      imgElement.src = "copy_done.png";
                      imgElement.alt = "Applied";
                      setTimeout(() => {
                          imgElement.src = "./apply.png";
                          imgElement.alt = "Apply";
                      }, 1000);
                  });
      
                  // Copy 버튼 클릭 기능 (이미지 클립보드 복사)
                  copyButton.addEventListener("click", async () => {
                      try {
                          const byteCharacters = atob(image.image_data);
                          const byteNumbers = new Array(byteCharacters.length);
                          for (let i = 0; i < byteCharacters.length; i++) {
                              byteNumbers[i] = byteCharacters.charCodeAt(i);
                          }
                          const byteArray = new Uint8Array(byteNumbers);
                          const blob = new Blob([byteArray], { type: "image/png" });
      
                          await navigator.clipboard.write([
                              new ClipboardItem({ "image/png": blob })
                          ]);
      
                          console.log(`이미지 ${index + 1}가 클립보드에 복사되었습니다!`);
                          
                          const imgElement = copyButton.querySelector("img");
                          imgElement.src = "copy_done.png";
                          imgElement.alt = "Copied";
                          setTimeout(() => {
                              imgElement.src = "./copy.png";
                              imgElement.alt = "Copy";
                          }, 1000);
      
                      } catch (error) {
                          console.error("❌ 이미지 복사 실패:", error);
                          alert("이미지 복사 중 오류가 발생했습니다.");
                      }
                  });

                  // source 버튼 클릭 기능
                  sourceButton.addEventListener("click", () => {
                    showSourceModal(image.source);

                    // 이미지 변경
                    const imgElement = sourceButton.querySelector("img");
                    imgElement.src = "copy_done.png";
                    imgElement.alt = "Source finish";
                        
                    setTimeout(() => {
                        imgElement.src = "./source.png";
                        imgElement.alt = "Source";
                    }, 1000);
                  });

                  // 스타일 적용
                  styleButtons(sourceButton);
                  styleButtons(copyButton);
                  styleButtons(applyButton);

                  // 버튼을 컨테이너에 추가
                  buttonContainer.appendChild(sourceButton);
                  buttonContainer.appendChild(copyButton);
                  buttonContainer.appendChild(applyButton);

                  // 이미지 요소 생성
                  const imgElement = document.createElement("img");
                  imgElement.src = `data:image/png;base64,${image.image_data}`;
                  imgElement.alt = `Chart ${index + 1}: ${image.file_name}`;
                  imgElement.style.maxWidth = "100%";
                  imgElement.style.borderRadius = "10px";
                  imgElement.style.marginTop = "40px";
                  imgElement.style.marginBottom = "22px"; // 이미지 하단 여백 조정
      
                  // 컨테이너에 이미지 및 버튼 추가
                  imageContainer.appendChild(leftIcon); // 항상 보이는 아이콘 추가
                  imageContainer.appendChild(buttonContainer); // 버튼 추가 (hover 시 표시)
                  imageContainer.appendChild(imgElement); // 이미지 추가
                  imageContainer.appendChild(timestamp); 
      
                  // 메시지 창에 이미지 컨테이너 추가
                  document.getElementById("chat-box").appendChild(imageContainer);

                  // 데이터 시각화 (Upload)옵션에서 답변 나오면 첨부한 csv파일 삭제
                  if (currentSelectedOption === "데이터 시각화 (Upload)") {
                    const fileCard = document.querySelector('.file-item');
                    if (fileCard) {
                        fileCard.remove();
                    }
                    existingCsvCount = 0;
                    checkCsvRequirement(currentSelectedOption);
                  }
                  
              });
          } else {
            botMessageElement.innerHTML = `
                 <img src="icon_circle.png" alt="FinPilot Icon" width="32" height="32" style="margin-right: 3px; vertical-align: middle;">
                 <br><span>이미지 데이터를 찾을 수 없습니다.</span>`;
          }
        } else {
            // 일반 텍스트 메시지 처리 (마크다운 파싱 적용)
            const botMessage = result.answer || "서버에서 응답을 받지 못했습니다.";
            const askTimeFormatted = new Date(new Date(result.ask_time).getTime() + 9 * 60 * 60 * 1000).toLocaleString("ko-KR") || "시간 정보 없음";
            // const askTimeFormatted = new Date(new Date(result.ask_time).getTime() + 9 * 60 * 60 * 1000)
                // .toLocaleString("ko-KR", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" }) || "시간 정보 없음";

            botMessageElement.innerHTML = `
                <img src="icon_circle.png" alt="FinPilot Icon" width="32" height="32" style="margin-right: 3px; vertical-align: middle;"> 
                <br><span>${marked.parse(botMessage)}</span>
                <br><small style="float: left; color: #888;">${askTimeFormatted}</small>`;
        }

        // Apply 버튼 추가
        const applyButton_ = document.createElement("button");
        applyButton_.classList.add("apply-btn");
        applyButton_.innerHTML = `<img src="./apply.png" alt="Apply" style="width: 16px; height: 16px;" title="Apply to Docs">`;
        botMessageElement.appendChild(applyButton_);

        // Copy 버튼 추가
        const copyButton_ = document.createElement("button");
        copyButton_.classList.add("copy-btn");
        copyButton_.innerHTML = `<img src="./copy.png" alt="Copy" style="width: 16px; height: 16px;" title="Copy">`;
        botMessageElement.appendChild(copyButton_);

        // source 버튼 추가
        const sourceButton_ = document.createElement("button");
        sourceButton_.classList.add("source-btn");
        sourceButton_.innerHTML = `<img src="./source.png" alt="Source" style="width: 16px; height: 16px;" title="Source">`;
        botMessageElement.appendChild(sourceButton_);

        // Apply 버튼 클릭 기능
        applyButton_.addEventListener("click", () => {
            appendToGoogleDoc(result.answer);
            
            // 이미지 변경
            const imgElement = applyButton_.querySelector("img");
            imgElement.src = "copy_done.png";
            imgElement.alt = "Applied";
                
            setTimeout(() => {
                imgElement.src = "./apply.png";
                imgElement.alt = "Apply";
            }, 1000);

        });

        // Copy 버튼 클릭 기능
        copyButton_.addEventListener("click", async () => { 
            copyElementToClipboard(botMessageElement);

            // 이미지 변경
            const imgElement = copyButton_.querySelector("img");
            imgElement.src = "copy_done.png";
            imgElement.alt = "Copied";

            setTimeout(() => {
                imgElement.src = "./copy.png";
                imgElement.alt = "Copy";
            }, 1000);
        });

        // source 버튼 클릭 기능
        sourceButton_.addEventListener("click", () => {
          showSourceModal(result.source);

          // 이미지 변경
          const imgElement = sourceButton_.querySelector("img");
          imgElement.src = "copy_done.png";
          imgElement.alt = "Source finish";
              
          setTimeout(() => {
              imgElement.src = "./source.png";
              imgElement.alt = "Source";
          }, 1000);
        });

        document.getElementById("chat-box").appendChild(botMessageElement);
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        console.error("❌ 오류:", error);
        alert("서버에서 답변을 가져오는 중 오류 발생.", error);
        hideLoadingUI(); // 오류 발생 시 로딩 UI 제거
    } finally {
        completeProgress(); // 🚀 서버 응답 도착 → 프로그레스 바 100% 도달
        setTimeout(() => {
            hideLoadingUI();
        }, 250); // 💡 UI 전환을 부드럽게 만들기 위해 0.25초 딜레이 추가
    }

    document.getElementById("user-input").value = ""; // 메시지 입력창 초기화
});

// "Shift + Enter" 키로 줄바꿈 및 "Enter" 키로 메시지 전송
document.getElementById("user-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        const inputField = document.getElementById("user-input");
        const cursorPosition = inputField.selectionStart;

        if (event.shiftKey) {
            // Shift + Enter 시 줄바꿈 및 들여쓰기 처리
            event.preventDefault(); // 기본 동작 방지

            // 글자 크기 15px 기준 약 55px 이동을 위한 공백 추가 
            const indentSpaces = "";  // 공백
            
            // 현재 커서 위치에 줄바꿈과 들여쓰기 삽입
            inputField.value = 
                inputField.value.substring(0, cursorPosition) + 
                "\n" + indentSpaces + 
                inputField.value.substring(cursorPosition);

            // 커서를 줄바꿈한 다음 위치로 이동
            inputField.selectionStart = inputField.selectionEnd = cursorPosition + 1 + indentSpaces.length;
        } else {
            // Enter 키로 메시지 전송
            event.preventDefault(); // 기본 동작 방지
            document.getElementById("send-btn").click(); // Send 버튼 클릭 동작 실행
        }
    }
});

// ----------------------------------------
// Google Docs에 텍스트 추가 (마크다운 적용 x)
// ----------------------------------------
function removeMarkdownSyntax(content) {
  return content.replace(/[#*]/g, ""); // '#'과 '*' 제거
}

async function appendToGoogleDoc(content) {
  showLoadingSpinner();
  try {
    const accessToken = await getAccessToken();
    const docInfoResponse = await fetch(
      `https://docs.googleapis.com/v1/documents/${DOCUMENT_ID}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );

    if (!docInfoResponse.ok) {
      const errorText = await docInfoResponse.text();
      throw new Error(`문서 정보 가져오기 실패: ${errorText}`);
    }

    const docInfo = await docInfoResponse.json();
    const contentLength = docInfo.body.content.length;
    console.log("문서 길이:", contentLength);

    // 마크다운 기호 제거
    const cleanedContent = removeMarkdownSyntax(content);

    const response = await fetch(
      `https://docs.googleapis.com/v1/documents/${DOCUMENT_ID}:batchUpdate`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          requests: [
            {
              insertText: {
                endOfSegmentLocation: {},
                text: `${cleanedContent}\n\n`,
              },
            },
          ],
        }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Google Docs 업데이트 실패: ${errorText}`);
    }

    console.log("✅ Google Docs 업데이트 성공!");
  } catch (error) {
    console.error("❌ Google Docs API 오류:", error);
    alert(`Google Docs 업데이트 중 문제가 발생했습니다: ${error.message}\n\nGoogle Docs 문서를 열고 다시 시도해주세요.`);
  } finally {
    hideLoadingSpinner();
  }
}

// ---------------------------------
// 클립보드에 HTML 콘텐츠 복사 함수
// ---------------------------------
async function copyElementToClipboard(element) {
  if (!element) {
      alert("복사할 내용이 없습니다.");
      return;
  }

  // 불필요한 요소 (아이콘, 버튼, 시간 등) 제거하고 클립보드에 복사할 내용 추출
  const clonedElement = element.cloneNode(true);

  // 필요 없는 요소 제거 (버튼, 아이콘, 시간 등)
  clonedElement.querySelectorAll("button, img[alt='FinPilot Icon'], small").forEach(el => el.remove());

  // 클립보드에 복사할 순수한 HTML 콘텐츠 가져오기
  const htmlContent = clonedElement.innerHTML;
  const blob = new Blob([htmlContent], { type: "text/html" });

  await navigator.clipboard.write([
      new ClipboardItem({ "text/html": blob })
  ]);
}

// ---------------------------------------------------------------------------------
// Google Docs에 이미지 추가 (Google Drive에 이미지를 업로드하고 Google Docs에 삽입)
// ---------------------------------------------------------------------------------
async function appendImageToGoogleDoc(base64Image, imageType = "image/png") {
    showLoadingSpinner();
    try {
        const accessToken = await getAccessToken(); // OAuth 2.0 액세스 토큰 가져오기

        // 1. FinPilot 폴더 ID 찾기 또는 생성
        const folderId = await getOrCreateFolder(accessToken, "FinPilot");

        // 2. Base64 데이터를 Blob으로 변환
        const byteCharacters = atob(base64Image);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: imageType });

        // 3. Google Drive에 이미지 업로드
        const metadata = {
            name: `uploaded_image_${Date.now()}.png`,
            mimeType: imageType,
            parents: [folderId]  // FinPilot 폴더에 저장
        };

        const formData = new FormData();
        formData.append("metadata", new Blob([JSON.stringify(metadata)], { type: "application/json" }));
        formData.append("file", blob);

        const uploadResponse = await fetch("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
            body: formData,
        });

        if (!uploadResponse.ok) {
            throw new Error("Google Drive 이미지 업로드 실패");
        }

        const uploadResult = await uploadResponse.json();
        const fileId = uploadResult.id;
        console.log("✅ Google Drive 업로드 성공! 파일 ID:", fileId);

        // 4. 공개 URL 만들기 (퍼블릭 공유 설정)
        await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}/permissions`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${accessToken}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                role: "reader",
                type: "anyone",
            }),
        });

        // 5. Google Docs에 이미지 추가 요청
        const imageUrl = `https://drive.google.com/uc?id=${fileId}`;
        const docResponse = await fetch(`https://docs.googleapis.com/v1/documents/${DOCUMENT_ID}:batchUpdate`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${accessToken}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                requests: [
                    {
                        insertInlineImage: {
                            endOfSegmentLocation: {},  // 문서 끝에 이미지 삽입
                            uri: imageUrl, // 업로드된 Google Drive 이미지 URL 사용
                            objectSize: {
                                width: {
                                    magnitude: 400,  // 너비 (픽셀)
                                    unit: "PT"        // 단위 (포인트)
                                },
                                height: {
                                    magnitude: 300,  // 높이 (픽셀)
                                    unit: "PT"
                                }
                            }
                        },
                    },
                ],
            }),
        });

        if (!docResponse.ok) {
            throw new Error(`Google Docs 이미지 추가 실패: ${await docResponse.text()}`);
        }

        console.log("✅ Google Docs 이미지 삽입 성공!");
        // alert("Google Docs에 이미지가 삽입되었습니다!");

    } catch (error) {
        console.error("❌ Google Docs API 오류:", error);
        alert(`Google Docs에 이미지를 삽입하는 중 문제가 발생했습니다: ${error.message}\n\nGoogle Docs 문서를 열고 다시 시도해주세요.`);
    } finally {
        hideLoadingSpinner();
    }
}

// FinPilot 폴더 확인 또는 생성 함수
async function getOrCreateFolder(accessToken, folderName) {
    try {
        // 폴더 검색 쿼리
        const searchResponse = await fetch(
            `https://www.googleapis.com/drive/v3/files?q=name='${folderName}' and mimeType='application/vnd.google-apps.folder' and trashed=false`,
            {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            }
        );

        if (!searchResponse.ok) {
            throw new Error("폴더 검색 실패");
        }

        const searchResult = await searchResponse.json();
        if (searchResult.files.length > 0) {
            console.log("폴더가 이미 존재함:", searchResult.files[0].id);
            return searchResult.files[0].id;
        }

        // 폴더가 없으면 생성
        const folderMetadata = {
            name: folderName,
            mimeType: "application/vnd.google-apps.folder",
        };

        const folderResponse = await fetch("https://www.googleapis.com/drive/v3/files", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${accessToken}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(folderMetadata),
        });

        if (!folderResponse.ok) {
            throw new Error("폴더 생성 실패");
        }

        const folderData = await folderResponse.json();
        console.log("폴더 생성 완료:", folderData.id);
        return folderData.id;

    } catch (error) {
        console.error("❌ 폴더 확인/생성 오류:", error);
        throw error;
    }
}

// 실시간으로 OAuth 토큰을 가져오기
async function getAccessToken() {
    return new Promise((resolve, reject) => {
      chrome.identity.getAuthToken({ interactive: true }, (token) => {
        if (chrome.runtime.lastError || !token) {
          reject(chrome.runtime.lastError || "Token을 가져올 수 없습니다.");
          return;
        }
        resolve(token);
      });
    });
}

// --------------------------------------------------------
// 📌 출처 버튼 기능 함수 (모달 UI + 출처 리스트 업데이트)
// --------------------------------------------------------
function showSourceModal(sourceData) {
  const sourceModal = document.getElementById("source-modal");
  const sourceList = document.getElementById("source-list");

  if (!sourceModal || !sourceList) {
      console.error("❌ ERROR: source-modal 또는 source-list를 찾을 수 없음.");
      return;
  }

  // 기존 리스트 초기화 후 새로운 출처 추가
  sourceList.innerHTML = sourceData
  .map((url) => {
    const shortUrl = url.length > 50 ? url.slice(0, 48) + ".." : url; // URL 길이가 50자 초과 시 줄이기
    const isValidUrl = url.startsWith("http://") || url.startsWith("https://"); // URL 형식 확인

    return `<li>
      <img src="link.png" alt="Link Icon" style="width: 14px; height: 14px; vertical-align: middle; margin-right: 5px;">
      ${isValidUrl ? `<a href="${url}" target="_blank" title="${url}">${shortUrl}</a>` : shortUrl}
    </li>`;
  })
  .join("");

  // ✅ 모달 표시 (hidden 클래스 제거)
  sourceModal.classList.remove("hidden");
}

// 📌 모달 닫기 기능 (닫기 버튼 및 바깥 클릭 시)
document.querySelector(".close").addEventListener("click", () => {
  document.getElementById("source-modal").classList.add("hidden");
});

window.addEventListener("click", (event) => {
  const sourceModal = document.getElementById("source-modal");
  if (event.target === sourceModal) {
      sourceModal.classList.add("hidden");
  }
});

// ---------------
//   환영 인사
// ---------------
document.addEventListener('DOMContentLoaded', () => {
  // Greeting 요소 가져오기
  const greetingElement = document.getElementById('greeting');

  // 저장된 userName 가져오기
  chrome.storage.local.get(['userName', 'isLoggedIn'], (data) => {
    if (data.isLoggedIn && data.userName) {
      // 로그인된 경우 환영 메시지 표시
      greetingElement.textContent = `${data.userName}님, 안녕하세요`;
      greetingElement.style.display = 'block';
      greetingElement.classList.remove('login-required'); // 흐림 클래스 제거
    } else {
      // 로그인되지 않은 경우
      greetingElement.textContent = `로그인이 필요합니다`;
      greetingElement.style.display = 'block';
      greetingElement.classList.add('login-required'); // 흐림 클래스 추가
      document.getElementById("user-input").disabled = true;
    }
  });
});

// ---------------------
//     파일 업로드
// ---------------------
// 파일 업로드 제한 조건
const MAX_FILES = 4; // 최대 파일 개수
const ALLOWED_EXTENSIONS = ['pdf', 'csv']; // 허용된 확장자
const MAX_CSV_FILES = 1; // .csv 파일 최대 개수
let existingCsvCount = 0; // CSV 파일 개수 추적 전역 변수

// 에러 메시지 표시 함수
const showErrorMessage = (message) => {
    const errorMessageDiv = document.getElementById('error-message');
    errorMessageDiv.textContent = message; // 에러 메시지 설정

    // 3초 후 에러 메시지 제거
    setTimeout(() => {
        errorMessageDiv.textContent = '';
    }, 3000);
};

// 파일 업로드 버튼 클릭 이벤트
document.getElementById('file_upload-btn').addEventListener('click', () => {
    document.getElementById('file-upload-input').click(); // 파일 선택 창 열기
});

// 파일 업로드 입력창 변경 이벤트
document.getElementById('file-upload-input').addEventListener('change', (event) => {
    const files = event.target.files; // 선택된 파일 목록
    const fileListDiv = document.getElementById('file-list'); // 파일 목록 표시 영역

    let existingFiles = fileListDiv.children.length; // 현재 업로드된 파일 수

    Array.from(files).forEach((file) => {
        const fileExtension = file.name.split('.').pop().toLowerCase(); // 파일 확장자

        // 파일 개수 제한 검사
        if (existingFiles >= MAX_FILES) {
            showErrorMessage(`최대 ${MAX_FILES}개의 파일만 업로드 가능합니다.`);
            return;
        }

        // 파일 확장자 검사 (PDF와 CSV만 허용)
        if (!ALLOWED_EXTENSIONS.includes(fileExtension)) {
            showErrorMessage(`.pdf와 .csv 파일만 업로드 가능합니다. (${file.name})`);
            return;
        }

        // .csv 파일 개수 제한 검사
        if (fileExtension === 'csv' && existingCsvCount >= MAX_CSV_FILES) {
          showErrorMessage(`.csv 파일은 최대 ${MAX_CSV_FILES}개까지 업로드 가능합니다. (${file.name})`);
          return;
        }

        // 파일 추가
        const fileCard = document.createElement('div');
        fileCard.classList.add('file-item');
        fileCard.textContent = file.name;

        // 삭제 버튼 추가
        const deleteBtn = document.createElement('button');
        deleteBtn.classList.add('delete-btn');
        deleteBtn.textContent = 'x';

        // 파일 삭제 버튼 클릭 이벤트
        deleteBtn.addEventListener('click', () => {
            fileCard.remove(); // 파일 카드 삭제
            existingFiles--; // 파일 개수 감소
            
            // CSV 파일 삭제 
            if (file.name.split('.').pop().toLowerCase() === 'csv') {
              existingCsvCount--;
              checkCsvRequirement(currentSelectedOption);
              delcsvToServer(file.name); 
            }

            // PDF 파일 삭제
            if (file.name.split('.').pop().toLowerCase() === 'pdf') {
              delPdfToServer(file.name); 
            }

        });

        fileCard.appendChild(deleteBtn);
        fileListDiv.appendChild(fileCard);
        existingFiles++; // 파일 개수 증가

        // csv 파일 카운트 증가
        if (fileExtension === 'csv') {
          existingCsvCount++;
          checkCsvRequirement(currentSelectedOption);  // 실시간으로 채팅창 상태 업데이트
          sendcsvToServer(file);
        }

        // PDF 파일만 서버로 전송
        if (fileExtension === 'pdf') {
          sendPdfToServer(file);
        }
        
    });

    // 업로드 입력 초기화 (중복 업로드 방지)
    event.target.value = '';
});

// 데이터 시각화 (Upload) 옵션 선택 시 CSV 파일 확인
function checkCsvRequirement(selectedOption) {
  const userInput = document.getElementById('user-input');

  if (selectedOption === "데이터 시각화 (Upload)") {
      if (existingCsvCount === 0) {  // existingCsvCount 사용
          showErrorMessage("해당 옵션은 .csv 파일 업로드 후 이용 가능합니다.");
          userInput.disabled = true;  // 입력 필드 비활성화
      } else {
          userInput.disabled = false;  // 입력 필드 활성화
      }
  } else {
      userInput.disabled = false; // 다른 옵션 선택 시 활성화
  }
}

// FastAPI 서버로 PDF 파일 전송 함수 (비동기 함수)
async function sendPdfToServer(file) {
  const formData = new FormData();

  // 사용자 이메일 및 문서 ID를 가져오는 함수
  const user_email = globalUserEmail;
  const docs_id = DOCUMENT_ID; // 문서 ID 

  // FormData에 이메일과 문서 ID 추가
  formData.append("user_email", user_email);
  formData.append("docs_id", docs_id);
  formData.append("file", file);

  // 버퍼링 시작
  showLoadingSpinner();

  try {
      const response = await fetch("https://finpilotback.duckdns.org/pdfs/", {
          method: 'POST',
          body: formData
      });

      if (!response.ok) {
          throw new Error("파일 업로드 실패");
      }

      const result = await response.json();
      console.log("서버 응답:", result);
  } catch (error) {
      console.error("서버 전송 실패:", error);
      alert(`PDF 파일 업로드 중 오류 발생: ${file.name}(${error.message})`);
  } finally{
    // 로딩 버퍼링 스피너 숨기기
    hideLoadingSpinner();
  }
}

// FastAPI 서버로 CSV 파일 전송 함수 (비동기 함수)
async function sendcsvToServer(file) {
  const formData = new FormData();

  // 사용자 이메일 및 문서 ID를 가져오는 함수
  const user_email = globalUserEmail;
  const docs_id = DOCUMENT_ID; // 문서 ID 

  // FormData에 이메일과 문서 ID 추가
  formData.append("user_email", user_email);
  formData.append("docs_id", docs_id);
  formData.append("file", file);

  // 버퍼링 시작
  showLoadingSpinner();

  try {
      const response = await fetch("https://finpilotback.duckdns.org/csvs/", {
          method: 'POST',
          body: formData
      });

      if (!response.ok) {
          throw new Error("파일 업로드 실패");
      }

      const result = await response.json();
      console.log("서버 응답:", result);
  } catch (error) {
      console.error("서버 전송 실패:", error);
      alert(`CSV 파일 업로드 중 오류 발생: ${file.name}(${error.message})`);
  } finally{
    // 로딩 버퍼링 스피너 숨기기
    hideLoadingSpinner();
  }
}

// FastAPI 서버의 PDF 파일 삭제 함수 (비동기 함수)
async function delPdfToServer(fileName) {
    const user_email = globalUserEmail;  // 전역 변수에서 사용자 이메일 가져오기
    const docs_id = DOCUMENT_ID;         // 문서 ID 가져오기
    
    const data = new URLSearchParams({
        user_email: user_email,
        docs_id: docs_id,
        file_name: fileName
    });

    // 버퍼링 시작
    showLoadingSpinner();

    try {
      const response = await fetch("https://finpilotback.duckdns.org/pdfs/", {
        method: 'DELETE',
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        body: data.toString(),
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "파일 삭제 실패");
      }
  
      const result = await response.json();
      console.log("서버 응답:", result);
      //alert(`PDF 파일 '${fileName}'이 서버에서 성공적으로 삭제되었습니다.`);
    } catch (error) {
      console.error("서버 연결 실패:", error);
      alert(`PDF 파일 삭제 중 오류 발생: ${fileName} (${error.message})`);
    } finally{
      hideLoadingSpinner();
    }
}

// FastAPI 서버의 CSV 파일 삭제 함수 (비동기 함수)
async function delcsvToServer(fileName) {
  const user_email = globalUserEmail;  // 전역 변수에서 사용자 이메일 가져오기
  const docs_id = DOCUMENT_ID;         // 문서 ID 가져오기

  // 요청할 JSON 데이터
  const data = new URLSearchParams({
    user_email: user_email,
    docs_id: docs_id,
    file_name: fileName
  });

  // 버퍼링 시작
  showLoadingSpinner();

  try {
    const response = await fetch("https://finpilotback.duckdns.org/csvs/", {
      method: 'DELETE',
      headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        body: data.toString(),
      });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "파일 삭제 실패");
    }

    const result = await response.json();
    console.log("서버 응답:", result);
    //alert(`CSV 파일 '${fileName}'이 서버에서 성공적으로 삭제되었습니다.`);
  } catch (error) {
    console.error("서버 연결 실패:", error);
    alert(`CSV 파일 삭제 중 오류 발생: ${fileName} (${error.message})`);
  } finally{
    hideLoadingSpinner();
  }
}

// ---------------------
//    채팅 옵션 선택
// ---------------------
// 드롭다운 버튼 및 메뉴 참조
const chatOptionButton = document.getElementById('chat_option-btn');
const chatOptionImage = chatOptionButton.querySelector('img');  // 이미지 요소 참조
const chatDropdownMenu = document.getElementById('chat-options-dropdown');
const selectedOptionDiv = document.getElementById('selected-option');

// 채팅 옵션별 이미지 매핑
const optionImages = {
  "초안 작성": "chat_option_1.png",
  "단락 생성": "chat_option_2.png",
  "요약 / 확장": "chat_option_3.png",
  "데이터 시각화 (Web)": "chat_option_4.png",
  "데이터 시각화 (Upload)": "chat_option_5.png"
};

// 기본값 설정
// currentSelectedOption을 if문 같은걸 사용해서 각 옵션마다 다른 이벤트를 주면 될듯
let currentSelectedOption = "단락 생성"; // 디폴트 값

// 기본값 화면 상단 표시
selectedOptionDiv.innerHTML = `
  <div style="position: relative;">
    <span>${currentSelectedOption}</span>
    <span id="info-icon" style="cursor: pointer; position: absolute; right: 0;">ⓘ</span>
  </div>`;

// 초기 이미지 설정
chatOptionImage.src = optionImages[currentSelectedOption];  

// 드롭다운 표시/숨김 토글
chatOptionButton.addEventListener('click', () => {
    chatDropdownMenu.classList.toggle('hidden'); // 숨김/표시 전환
});

// ✅ 바깥 영역 클릭 시 드롭다운 닫기
window.addEventListener("click", (event) => {
  if (
      !chatDropdownMenu.contains(event.target) && // 드롭다운 내부 클릭 X
      !chatOptionButton.contains(event.target) && // 버튼 클릭 X
      !chatDropdownMenu.classList.contains('hidden') // 드롭다운이 열려 있을 때만
  ) {
      chatDropdownMenu.classList.add('hidden'); // ❗ 'hidden' 클래스 추가 (무조건 닫기)
  }
});

// 각 옵션 클릭 시 동작
const dropdownItems = document.querySelectorAll('.dropdown-item');
dropdownItems.forEach((item) => {
    item.addEventListener('click', () => {
        // 모든 항목에서 선택 상태 제거
        dropdownItems.forEach((i) => i.classList.remove('selected'));

        // 클릭된 항목에 선택 상태 추가
        item.classList.add('selected');

        // 선택된 옵션 업데이트
        // const currentSelectedOption = item.textContent.trim(); // 항목의 텍스트 가져오기
        currentSelectedOption = item.textContent.trim(); 
        
        // 화면 상단에 표시
        selectedOptionDiv.innerHTML = `
          <div style="position: relative;">
            <span>${currentSelectedOption}</span>
            <span id="info-icon" style="cursor: pointer; position: absolute; right: 0;">ⓘ</span>
          </div>`;

        // 버튼 이미지 변경
        if (optionImages[currentSelectedOption]) {
          chatOptionImage.src = optionImages[currentSelectedOption];
        }

        // 드롭다운 메뉴 숨기기
        chatDropdownMenu.classList.add('hidden');

        // CSV 파일 확인
        checkCsvRequirement(currentSelectedOption); 

        // ⓘ 아이콘 이벤트 연결
        attachInfoIconEvent();
    });
});

// ⓘ 아이콘 클릭 이벤트 연결 함수
function attachInfoIconEvent() {
    const infoIcon = document.getElementById("info-icon");
    infoIcon.addEventListener("click", () => {
        // 단일 info URL로 이동
        chrome.tabs.create({ url: "./web/info/info.html" });
    });
}
// 페이지 로드 시 ⓘ 아이콘 이벤트 연결
attachInfoIconEvent();
