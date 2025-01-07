document.addEventListener('DOMContentLoaded', () => {
    // 버튼 요소 찾기
    const GloginButton = document.getElementById('GloginButton');
  
    if (GloginButton) {
      // 클릭 이벤트 추가
      GloginButton.addEventListener('click', () => {
        // alert('Google 로그인 버튼 클릭됨!');  // 그냥 구글 로그인 클릭 디버깅
        // 로그인 로직을 여기에 추가
        chrome.runtime.sendMessage({ message: 'Glogin' }, (response) => {
          if (response && response.success) {
            alert(`${response.name} (${response.email}) 님 안녕하세요!`);

            // 현재 탭에서 web/start/start.html로 이동
            window.location.href = '/web/start/start.html';
          } else {
            alert('Google 로그인 실패! 다시 시도해주세요.');
          }
        });
      });
    } else {
      console.error('Google Login Button을 찾을 수 없습니다.');
    }
  });
  