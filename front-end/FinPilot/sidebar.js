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
            fetch('http://finpilotback.duckdns.org:8000/sessions/', {
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
    showLoadingSpinner();

    try {
        const requestData = {
            user_email: globalUserEmail,
            docs_id: DOCUMENT_ID,
            question: userInput,
            chat_option: currentSelectedOption
        };

        const response = await fetch("http://finpilotback.duckdns.org:8000/qnas/", {
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

                  // 스타일 적용
                  styleButtons(copyButton);
                  styleButtons(applyButton);

                  // 버튼을 컨테이너에 추가
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

            botMessageElement.innerHTML = `
                <img src="icon_circle.png" alt="FinPilot Icon" width="32" height="32" style="margin-right: 3px; vertical-align: middle;"> 
                <br><span>${marked.parse(botMessage)}</span>
                <br><small style="float: right; color: #888;">${askTimeFormatted}</small>`;
        }

        // Apply 버튼 추가
        const applyButton = document.createElement("button");
        applyButton.classList.add("apply-btn");
        applyButton.innerHTML = `<img src="./apply.png" alt="Apply" style="width: 16px; height: 16px;" title="Apply to Docs">`;
        botMessageElement.appendChild(applyButton);

        // Copy 버튼 추가
        const copyButton = document.createElement("button");
        copyButton.classList.add("copy-btn");
        copyButton.innerHTML = `<img src="./copy.png" alt="Copy" style="width: 16px; height: 16px;" title="Copy">`;
        botMessageElement.appendChild(copyButton);

        // Apply 버튼 클릭 기능
        applyButton.addEventListener("click", () => {
            if (currentSelectedOption === "데이터 시각화 (Web)" || currentSelectedOption === "데이터 시각화 (Upload)") {
                // Google Docs에 이미지 삽입 기능
                result.images.forEach((image) => {
                    appendImageToGoogleDoc(image.image_data, "image/png");
                });
            } else {appendToGoogleDoc(result.answer);}
    
            const imgElement = applyButton.querySelector("img");
            imgElement.src = "copy_done.png";
            imgElement.alt = "Applied";
                
            setTimeout(() => {
                imgElement.src = "./apply.png";
                imgElement.alt = "Apply";
            }, 1000);

        });

        // Copy 버튼 클릭 기능
        copyButton.addEventListener("click", async () => { 
            if (currentSelectedOption === "초안 작성" || currentSelectedOption === "단락 생성" || currentSelectedOption === "요약 / 확장") {
                navigator.clipboard.writeText(result.answer).then(() => {
                    console.log("응답이 클립보드에 복사되었습니다!");
                })
            }else{
                try {
                    // 이미지 Base64 데이터를 Blob으로 변환
                    const base64Data = result.images[0].image_data; // 첫 번째 이미지 사용
                    const byteCharacters = atob(base64Data);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
    
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], { type: "image/png" });
    
                    // 클립보드에 이미지 복사
                    await navigator.clipboard.write([
                        new ClipboardItem({
                            "image/png": blob
                        })
                    ]);
    
                    console.log("이미지가 클립보드에 복사되었습니다!");
                } catch (error) {
                    console.error("❌ 이미지 복사 실패:", error);
                }
            }
            // 이미지 변경
            const imgElement = copyButton.querySelector("img");
            imgElement.src = "copy_done.png";
            imgElement.alt = "Copied";

            setTimeout(() => {
                imgElement.src = "./copy.png";
                imgElement.alt = "Copy";
            }, 1000);
        });

        document.getElementById("chat-box").appendChild(botMessageElement);
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        console.error("❌ 오류:", error);
        alert("서버에서 답변을 가져오는 중 오류 발생.");
    } finally {
        hideLoadingSpinner();
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
// Google Docs에 텍스트 추가 (마크다운 적용)
// ----------------------------------------
async function appendToGoogleDoc(markdownContent) {
  showLoadingSpinner();
  try {
    const accessToken = await getAccessToken();

    // 문서 끝 위치 가져오기
    const docInfoResponse = await fetch(
      `https://docs.googleapis.com/v1/documents/${DOCUMENT_ID}`,
      {
        method: "GET",
        headers: { Authorization: `Bearer ${accessToken}` },
      }
    );

    if (!docInfoResponse.ok) {
      throw new Error("문서 정보 가져오기 실패");
    }

    const docInfo = await docInfoResponse.json();
    let endIndex = docInfo.body.content.length > 1
      ? docInfo.body.content[docInfo.body.content.length - 1].endIndex - 1
      : 1;

    // 마크다운을 HTML로 변환 후 텍스트 추출
    const htmlContent = marked.parse(markdownContent);
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = htmlContent;

    let requests = [];
    let currentIndex = endIndex;

    function parseElement(element) {
      if (element.nodeType === Node.TEXT_NODE) {
        const text = element.textContent.trim();
        if (text.length > 0) {
          requests.push({
            insertText: {
              location: { index: currentIndex },
              text: text + "\n",
            },
          });

          currentIndex += text.length + 1;  // 개행 포함
        }
      } else if (element.nodeType === Node.ELEMENT_NODE) {
        element.childNodes.forEach(parseElement);

        // 텍스트 스타일 적용 (제목, 굵기, 기울임)
        let startIdx = currentIndex - element.innerText.length;
        let endIdx = currentIndex;

        if (element.tagName === "B" || element.tagName === "STRONG") {
          requests.push({
            updateTextStyle: {
              range: { startIndex: startIdx, endIndex: endIdx },
              textStyle: { bold: true },
              fields: "bold",
            },
          });
        } else if (element.tagName === "I" || element.tagName === "EM") {
          requests.push({
            updateTextStyle: {
              range: { startIndex: startIdx, endIndex: endIdx },
              textStyle: { italic: true },
              fields: "italic",
            },
          });
        } else if (element.tagName === "H1") {
          requests.push({
            updateParagraphStyle: {
              range: { startIndex: startIdx, endIndex: endIdx },
              paragraphStyle: { namedStyleType: "HEADING_1" },
              fields: "namedStyleType",
            },
          });
        } else if (element.tagName === "H2") {
          requests.push({
            updateParagraphStyle: {
              range: { startIndex: startIdx, endIndex: endIdx },
              paragraphStyle: { namedStyleType: "HEADING_2" },
              fields: "namedStyleType",
            },
          });
        } else if (element.tagName === "UL") {
          element.querySelectorAll("li").forEach((li) => {
            requests.push({
              insertText: {
                location: { index: currentIndex },
                text: "• " + li.innerText + "\n",
              },
            });
            currentIndex += li.innerText.length + 3;
          });
        } else if (element.tagName === "OL") {
          let counter = 1;
          element.querySelectorAll("li").forEach((li) => {
            requests.push({
              insertText: {
                location: { index: currentIndex },
                text: `${counter}. ${li.innerText}\n`,
              },
            });
            currentIndex += li.innerText.length + 3;
            counter++;
          });
        } else if (element.tagName === "BLOCKQUOTE") {
          requests.push({
            updateParagraphStyle: {
              range: { startIndex: startIdx, endIndex: endIdx },
              paragraphStyle: {
                indentStart: { magnitude: 30, unit: "PT" },
                borderLeft: {
                  color: { rgbColor: { red: 0.2, green: 0.2, blue: 0.2 } },
                  width: { magnitude: 2, unit: "PT" },
                },
              },
              fields: "indentStart,borderLeft",
            },
          });
        }
      }
    }

    // HTML 요소를 순회하며 파싱
    tempDiv.childNodes.forEach(parseElement);

    if (requests.length === 0) {
      throw new Error("추출된 텍스트가 없습니다.");
    }

    // Google Docs API 요청 실행
    const response = await fetch(
      `https://docs.googleapis.com/v1/documents/${DOCUMENT_ID}:batchUpdate`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ requests }),
      }
    );

    if (!response.ok) {
      throw new Error(`Google Docs 업데이트 실패: ${await response.text()}`);
    }

    console.log("✅ Google Docs 마크다운 적용 성공!");
    alert("Google Docs에 마크다운 형식으로 적용되었습니다!");

  } catch (error) {
    console.error("❌ Google Docs API 오류:", error);
    alert(`Google Docs 업데이트 중 문제가 발생했습니다: ${error.message}`);
  } finally {
    hideLoadingSpinner();
  }
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
      const response = await fetch("http://finpilotback.duckdns.org:8000/pdfs/", {
          method: 'POST',
          body: formData
      });

      if (!response.ok) {
          throw new Error("파일 업로드 실패");
      }

      const result = await response.json();
      console.log("서버 응답:", result);
  
      //alert(`PDF 파일 '${file.name}'이 서버에 성공적으로 업로드되었습니다.`); // 없앨지 말지 고민 중..
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
      const response = await fetch("http://finpilotback.duckdns.org:8000/csvs/", {
          method: 'POST',
          body: formData
      });

      if (!response.ok) {
          throw new Error("파일 업로드 실패");
      }

      const result = await response.json();
      console.log("서버 응답:", result);
      //alert(`CSV 파일 '${file.name}'이 서버에 성공적으로 업로드되었습니다.`); // 없앨지 말지 고민 중..
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
      const response = await fetch("http://finpilotback.duckdns.org:8000/pdfs/", {
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
    const response = await fetch("http://finpilotback.duckdns.org:8000/csvs/", {
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
