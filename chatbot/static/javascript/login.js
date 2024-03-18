document.addEventListener('DOMContentLoaded', (event) => {
  // 에러 메시지를 포함하는 모든 요소 선택
  const errorMessages = document.querySelectorAll('.error-message');

  // 각 에러 메시지에 대해 일정 시간(예: 5000ms = 5초) 후에 숨김 처리
  errorMessages.forEach((errorMsg) => {
      setTimeout(() => {
          // 에러 메시지 요소 숨기기
          errorMsg.style.display = 'none';
      }, 5000); // 5000ms = 5초 후에 에러 메시지 숨김
  });
});
