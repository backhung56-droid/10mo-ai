'use strict';
// 별도 백엔드·개인정보 수집 없음: 신청은 사용자 제공 Google Form URL로 직접 이동합니다.
(function(){
  const params = new URLSearchParams(window.location.search);
  const allowed = ['utm_source', 'utm_medium', 'utm_campaign'];
  // 추적 파라미터는 신청 폼 URL에 임의로 덧붙이지 않습니다.
  const links = document.querySelectorAll('[data-apply]');
  links.forEach(link => link.addEventListener('click', () => {
    // 확장 지점: 사용자가 실제 분석 시스템을 연결한 경우에만 측정 코드를 추가합니다.
  }));
})();
