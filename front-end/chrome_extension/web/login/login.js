// Google 로그인 //
document.addEventListener('DOMContentLoaded', () => {
  // 버튼 요소 찾기
  const GloginButton = document.getElementById('GloginButton');

  if (GloginButton) {
    // 클릭 이벤트 추가
    GloginButton.addEventListener('click', () => {
      chrome.runtime.sendMessage({ message: 'Glogin' }, (response) => {
        if (response && response.success) {
          alert(`${response.name} (${response.email}) 님 안녕하세요!`);

          // 로그인 성공 시 상태 업데이트     
          chrome.storage.local.set({ 
            isLoggedIn: true,
            userEmail: response.email, // 이메일 저장
            userName: response.name, // 이름 저장
            authToken: response.token, // 토큰 저장
            userProfile: response.picture // 프로필 사진 URL 저장 
          }, () => {
            console.log('Login state set to true and email saved.');
            console.log('Google Login Response:', response);
          });

          // 현재 탭에서 web/start/start.html로 이동
          window.location.href = '/web/start/start.html';
        } else {
          alert('Google 로그인 실패! 다시 시도해주세요.');
          // 로그인 실패 시 상태 초기화
          chrome.storage.local.set({ isLoggedIn: false }, () => {
            console.log('Login state set to false.');
          });
        }
      });
    });
  } else {
    console.error('Google Login Button을 찾을 수 없습니다.');
  }
});
