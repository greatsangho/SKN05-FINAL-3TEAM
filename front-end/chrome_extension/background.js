// Google Login
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.message === 'Glogin') {
    // Auth Token 요청
    chrome.identity.getAuthToken({ interactive: true }, (token) => {
      if (chrome.runtime.lastError) {
        console.error('Google 로그인 실패:', chrome.runtime.lastError);
        sendResponse({ success: false });
        return;
      }

      // 토큰을 사용해 사용자 정보 가져오기
      fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.email) {
            sendResponse({
              success: true,
              email: data.email,
              name: data.name,
              picture: data.picture, // 프로필 사진 URL 추가
            });
          } else {
            sendResponse({ success: false });
          }
        })
        .catch((error) => {
          console.error('사용자 정보 가져오기 실패:', error);
          sendResponse({ success: false });
        });
    });

    // 비동기 응답을 명시
    return true;
  }
});


// 구글 Docs페이지로 넘어가기
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'openGoogleDocs') {
    chrome.tabs.update(sender.tab.id, { url: 'https://docs.google.com' });
    sendResponse({ success: true });
  }
});


// 로그인 유무에 따라 페이지 디렉션하기
chrome.action.onClicked.addListener(() => {
  chrome.storage.local.get("isLoggedIn", (data) => {
    if (data.isLoggedIn) {
      // 로그인 상태: 팝업 페이지 열기
      chrome.action.setPopup({ popup: "./popup.html" });
      chrome.action.openPopup(); // 팝업 창 열기
    } else {
      // 비로그인 상태: 랜딩 페이지 새 탭으로 열기
      chrome.tabs.create({ url: "./web/landing/landing.html" });
    }
  });
});

// 커서때매 씀
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});





