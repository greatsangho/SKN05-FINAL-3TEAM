// Log Out 버튼
document.getElementById("logoutButton").addEventListener("click", () => {
    // Google 로그아웃 URL을 호출하여 세션 종료
    fetch("https://accounts.google.com/Logout", { mode: "no-cors" })
      .then(() => {
        // 1. 로그아웃 상태 업데이트
        chrome.storage.local.set({ isLoggedIn: false, userEmail: null }, () => {
          console.log("User logged out and status updated to false");
          const emailElement = document.querySelector('.email');
          emailElement.textContent = 'Not logged in'; // 초기 상태로 업데이트
  
          // 2. 로그아웃 후 랜딩 페이지로 리다이렉트
          chrome.tabs.create({ url: "./web/landing/landing.html" });
        });
      })
      .catch((error) => {
        console.error("Logout failed:", error);
      });
  });
  

// Open Docs버튼, Get Help 버튼
document.addEventListener("DOMContentLoaded", () => {
    // Open Docs 버튼 클릭 이벤트
    const openDocsButton = document.getElementById("opendocsButton");
    if (openDocsButton) {
      openDocsButton.addEventListener("click", () => {
        // 새 탭에서 Google Docs 페이지 열기
        chrome.tabs.create({ url: "https://docs.google.com/document" });
      });
    }
  
    // Get Help 버튼 클릭 이벤트
    const helpButton = document.getElementById("helpButton");
    if (helpButton) {
      helpButton.addEventListener("click", () => {
        // 새 탭에서 landing.html 열기
        chrome.tabs.create({ url: "./web/landing/landing.html" });
      });
    }
});


// google email 표시
document.addEventListener('DOMContentLoaded', () => {
  const emailElement = document.querySelector('.email'); // 이메일 표시 요소

  // Chrome Storage에서 이메일 가져오기
  chrome.storage.local.get('userEmail', (data) => {
    if (data.userEmail) {
      // 저장된 이메일이 있다면 업데이트
      emailElement.textContent = data.userEmail;
    } else {
      // 저장된 이메일이 없으면 기본 메시지 표시
      emailElement.textContent = 'Not logged in';
    }
  });
});
