let DOCUMENT_ID = ""; // 초기값 설정

// Google 서비스 계정 JSON 키 정보 (각자 개인의 키를 넣어주세요!!!!!!!!!!!!!!)
const serviceAccount = {};
// OpenAI API (키 각자 개인의 키를 넣어주세요!!!!!!!!!!!!!!!!!!)
const OPENAI_API_KEY ="sk-proj--";   

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
        reject("Google Docs 문서 ID를 URL에서 찾을 수 없습니다.");
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const docId = await getDocumentIdFromActiveTab();
    if (docId) {
      DOCUMENT_ID = docId;
      console.log(`문서 ID 자동 추출 성공: ${DOCUMENT_ID}`);
      alert(`Google Docs 문서가 연동되었습니다.\n\n문서 ID: ${DOCUMENT_ID}`);  // 활성 탭이 구글 docs라서 정상적으로 문서 id를 가져왔을 때
    }
  } catch (error) {
    console.error("문서 ID 추출 실패:", error);
    // 지금 활성화된 탭이 구글 docs가 아니라서 문서 id를 제대로 못 가져올 때
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

// "Send" 버튼 클릭 이벤트
document.getElementById("send-btn").addEventListener("click", async () => {
  const userInput = document.getElementById("user-input").value.trim();
  // 사용자 메시지가 비어있는 경우 중단
  if (!userInput) {
    alert("질문을 입력해주세요.");
    return;
  }

  const chatBox = document.getElementById("chat-box");

  // 사용자 메시지 생성
  const userMessage = document.createElement("div");
  userMessage.classList.add("chat-message", "question"); // 사용자 메시지에 클래스 추가
  userMessage.textContent = `${userInput}`; //🧑‍💻
  chatBox.appendChild(userMessage);

  // 로딩 스피너 표시
  showLoadingSpinner();

  try {
    // GPT 호출
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "gpt-4",
        messages: [{ role: "user", content: userInput }],
      }),
    });

    if (!response.ok) throw new Error("GPT API 호출 실패");

    const data = await response.json();
    const botMessage = data.choices[0]?.message?.content || "GPT 응답 실패";

    // GPT 응답 메시지 생성
    const botMessageElement = document.createElement("div");
    botMessageElement.classList.add("chat-message", "answer"); // GPT 메시지에 클래스 추가
    botMessageElement.innerHTML = `
    <img src="icon_circle.png" alt="FinPilot Icon" width="32" height="32" style="margin-right: 3px; vertical-align: middle;">
    <span>${botMessage}</span>`; // FinPilot 로고

    chatBox.appendChild(botMessageElement);

    await appendToGoogleDoc(botMessage); // Google Docs에 추가

    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (error) {
    console.error("❌ 오류:", error);
  } finally {
    // 로딩 버퍼링 스피너 숨기기
    hideLoadingSpinner();
  }

  document.getElementById("user-input").value = ""; // 메시지 입력창 초기화
});

// "Enter" 키로 전송 이벤트 구현
document.getElementById("user-input").addEventListener("keyup", (event) => {
  if (event.key === "Enter") {
    event.preventDefault(); // 기본 Enter 동작 방지
    document.getElementById("send-btn").click(); // Send 버튼 클릭 동작 실행
  }
});

// Google Docs API로 응답 추가
async function appendToGoogleDoc(content) {
  try {
    const accessToken = await getAccessToken();

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
                location: { index: 1 },
                text: `${content}\n`,
              },
            },
          ],
        }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`❌ Google Docs 업데이트 실패: ${errorText}`);
    }

    console.log("✅ Google Docs 업데이트 성공!");
  } catch (error) {
    console.error("❌ Google Docs API 오류:", error);
    alert(
      "연동된 문서를 찾을 수 없습니다. 활성 탭의 Google Docs URL이 올바른지 확인해주세요. 또한, 문서에 서비스 계정에 대한 편집 권한을 공유했는지 확인해주세요.\n\n" +
        "- 올바른 URL 예시:\n  https://docs.google.com/document/d/문서ID/edit\n\n" +
        "- 편집자 권한 공유 방법:\n" +
        "  1. Google Docs 문서를 열고 우측 상단의 '공유' 버튼을 클릭합니다.\n" +
        "  2. 아래 이메일을 추가하여 편집자 권한을 부여하세요.\n" +
        "     - 서비스 계정 이메일: finpilot@gen-lang-client-0845052581.iam.gserviceaccount.com\n\n" +
        "오류가 계속된다면 사이드 패널을 닫고 Google Docs에 재접속한 후 다시 실행해주세요."
    );
  }
}

// JWT 토큰 생성 및 Google OAuth 2.0 토큰 요청
async function getAccessToken() {
  const header = {
    alg: "RS256",
    typ: "JWT",
  };

  const now = Math.floor(Date.now() / 1000);
  const claims = {
    iss: serviceAccount.client_email,
    scope: "https://www.googleapis.com/auth/documents",
    aud: serviceAccount.token_uri,
    exp: now + 3600,
    iat: now,
  };

  const encodeBase64URL = (obj) =>
    btoa(JSON.stringify(obj))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

  const headerEncoded = encodeBase64URL(header);
  const claimsEncoded = encodeBase64URL(claims);
  const unsignedToken = `${headerEncoded}.${claimsEncoded}`;

  try {
    const keyBuffer = pemToArrayBuffer(serviceAccount.private_key);

    const privateKey = await crypto.subtle.importKey(
      "pkcs8",
      keyBuffer,
      {
        name: "RSASSA-PKCS1-v1_5",
        hash: { name: "SHA-256" },
      },
      false,
      ["sign"]
    );

    const signature = await crypto.subtle.sign(
      "RSASSA-PKCS1-v1_5",
      privateKey,
      new TextEncoder().encode(unsignedToken)
    );

    const signatureEncoded = btoa(
      String.fromCharCode(...new Uint8Array(signature))
    )
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

    const jwt = `${unsignedToken}.${signatureEncoded}`;

    const response = await fetch(serviceAccount.token_uri, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
        assertion: jwt,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`OAuth 2.0 토큰 요청 실패: ${errorText}`);
    }

    const { access_token } = await response.json();
    return access_token;
  } catch (error) {
    console.error("❌ JWT 생성 또는 토큰 요청 중 오류:", error);
  }
}

// 🔑 PEM 형식의 키를 ArrayBuffer로 변환
function pemToArrayBuffer(pem) {
  const base64 = pem
    .replace(/-----BEGIN PRIVATE KEY-----/, "")
    .replace(/-----END PRIVATE KEY-----/, "")
    .replace(/\n/g, "");
  const binary = atob(base64);
  const buffer = new ArrayBuffer(binary.length);
  const view = new Uint8Array(buffer);
  for (let i = 0; i < binary.length; i++) {
    view[i] = binary.charCodeAt(i);
  }
  return buffer;
}