// 확장 프로그램 아이콘 클릭하면 원하는 페이지로 넘어가기
chrome.action.onClicked.addListener(() => {
  chrome.tabs.create({
    // url: chrome.runtime.getURL("./web/login/login.html") // 로그인
    url: chrome.runtime.getURL("./web/landing/landing.html") // 랜딩
  });
});

// Google Login
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.message === 'Glogin') {
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





