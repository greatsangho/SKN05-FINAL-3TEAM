// Log Out 버튼
document.getElementById("logoutButton").addEventListener("click", () => {
    // Google 로그아웃 URL을 호출하여 세션 종료
    fetch("https://accounts.google.com/Logout", { mode: "no-cors" })
      .then(() => {
        // 1. 로그아웃 상태 업데이트
        chrome.storage.local.set({ isLoggedIn: false, userEmail: null, userProfile:null, userName:null }, () => {
          console.log("User logged out and status updated to false");

          // 이름 초기화
          const greetingElement = document.getElementById('greeting');
          if (greetingElement) {
            greetingElement.style.display = 'none'; // 숨기기
          }

          // 이메일 초기화
          const emailElement = document.querySelector('.email');
          emailElement.textContent = 'Not logged in'; // 초기 상태로 업데이트

          // 프사 초기화
          const profileElement = document.getElementById('userProfile');
          profileElement.src = "./default_profile.webp"; // 기본 이미지로 설정    
          profileElement.style.display = 'block'; // 필요 시 표시 
  
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

// 이메일이랑 프사 표시
chrome.storage.local.get(['userEmail', 'userProfile'], (data) => {

  const emailElement = document.querySelector('.email');
  const profileElement = document.getElementById('userProfile');

  if (data.userEmail) {
    emailElement.textContent = data.userEmail;
  } else {
    emailElement.textContent = 'Not logged in';
  }

  if (data.userProfile) {
    profileElement.src = data.userProfile;
    profileElement.style.display = 'block';
  } else {
    profileElement.src = "./default_profile.webp";
  }
});

