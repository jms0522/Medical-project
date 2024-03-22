const messagesList = document.querySelector('.messages-list');
const messageForm = document.querySelector('.message-form');
const messageInput = document.querySelector('.message-input');
const submitButton = document.querySelector("button[type='submit']"); // 폼 제출 버튼 선택

function disableSubmitButton() {
    console.log('disableSubmitButton')
  submitButton.disabled = true; // 버튼을 비활성화
}
function enableSubmitButton() {
    console.log('enableSubmitButton')
  submitButton.disabled = false; // 버튼을 활성화
}
function showLoader() {
    document.querySelector('.loading-bar').style.display = 'flex'; // 로딩바 온
}
function hideLoader() {
    document.querySelector('.loading-bar').style.display = 'none'; // 로딩바 오프
}

// 스크롤 하단 이동 함수
function scrollToBottom() {
    const messagesEnd = document.createElement('div');
    messagesList.scrollTop = messagesList.scrollHeight;
    messagesList.appendChild(messagesEnd);
    messagesEnd.scrollIntoView({ behavior: 'smooth' });
}

// 기본 질문 처리 로직(질문 내용 화면 출력 및 api호출)
document.addEventListener('DOMContentLoaded', function() {
    const messagesList = document.querySelector('.messages-list');
    const messageForm = document.querySelector('.message-form');
    const messageInput = document.querySelector('.message-input');

    function sendMessage(message) {
        // 사용자 메시지 화면에 표시 (질문 양식 사용)
        const messageItem = document.createElement('li');
        const messageMarkdown = message.replace(/\\"/g, '`');
        const messageHtml = marked.parse(messageMarkdown);
        messageItem.classList.add('message', 'sent');
        messageItem.innerHTML = `
        <div class="message-item message-sender">
            <div class="message-content">
                <b>You</b>
                <div class="message-line"></div>
                <div class="message-text">${messageHtml}</div>
            </div>
        </div>`;
        messagesList.appendChild(messageItem);
    }

    // <textarea>에 대한 keydown 이벤트 리스너 추가
    messageInput.addEventListener('keydown', function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault(); // 기본 동작(줄 바꿈)을 막음
            // 폼 제출 로직
            messageForm.dispatchEvent(new Event('submit', {cancelable: true})); // 폼 제출 이벤트 강제 발생
        }
    });

    if (messageForm) {
        messageForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const message = messageInput.value.trim();
            if (message.length === 0) {
                return;
            }
            disableSubmitButton(); // 답변 생성 시작 시 버튼 비활성화
            scrollToBottom(); // 데이터 처리 완료 후 스크롤 하단으로 이동
            showLoader(); // 비동기 작업 시작 전 로더 표시
            // 서버로 데이터 전송
            fetch('/ask_question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: new URLSearchParams({ 'text': message })
            })
            .then(response => {
                if (response.status === 403) {
                    // 403 상태 코드인 경우, 로그인 페이지로 리다이렉트
                    alert("로그인이 필요합니다.");
                    return Promise.reject("로그인이 필요합니다."); // 이후 처리 중단
                }
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(text => {
                sendMessage(message); // 사용자 메시지 화면에 표시
                const data = JSON.parse(text); // JSON 형식인 경우 파싱
                processServerResponse(data);
                scrollToBottom(); // 데이터 처리 완료 후 스크롤 하단으로 이동
            })
            .catch(error => {
                console.error('Fetch error:', error);
            })
            .finally(() => {
                hideLoader(); // 작업 완료 후 로더 숨김
                enableSubmitButton(); // 이제 여기에서 버튼을 활성화
                messageInput.value = ''; // 입력 필드 초기화
            });
        });
    }
});

// 기본 답변 로직(답변 내용 화면 출력)
function processServerResponse(data) {
    const responseText = data.data; 
    const questionId = data.id;
    const responseTextMarkdown = responseText.replace(/\\"/g, '`');
    const responseTextHtml = marked.parse(responseTextMarkdown);
    
    // 답변 항목 생성
    const messageItem = document.createElement('li');
    messageItem.classList.add('message', 'received');
    messageItem.innerHTML = `
    <div class="message-item message-receiver">
        <div class="message-content">
            <b>Dr.RC</b>
            <div class="message-line"></div>
            <div class="message-text">${responseTextHtml}
            </div>
        </div>
        <div class="message-line"></div>
        <div class="similar-answers-section"></div>
    </div>`;
    addSimilarAnswersButton(messageItem, questionId); // 유사 답변 버튼 추가
    messagesList.appendChild(messageItem);
    scrollToBottom();
}

// 유사 답변 버튼 생성 
function addSimilarAnswersButton(messageItem, questionId) {
    const messageContent = messageItem.querySelector('.message-content');
    const similarAnswersButton = document.createElement('button');
    similarAnswersButton.textContent = "유사 답변 보기";
    similarAnswersButton.classList.add("text-lg", 'font-bold', 'border-4', 'border-white'
    );
    similarAnswersButton.setAttribute('data-question-id', questionId);
    similarAnswersButton.addEventListener('click', function() {
        showSimilarAnswers(questionId, messageItem);
    });
    messageContent.appendChild(similarAnswersButton);
}

// 유사 답변 내용 출력
function showSimilarAnswers(questionId, messageItem) {
    console.log("showSimilarAnswers called with", questionId);
    const url = `/similar-answers/${questionId}/`;
    disableSubmitButton(); // 답변 생성 시작 시 버튼 비활성화
    showLoader(); // 비동기 작업 시작 전 로더 표시
    fetch(url, {
        method: 'GET', // GET 메소드 사용
        headers: {
            'Content-Type': 'application/json', // JSON 형태의 데이터를 요청
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // 서버로부터 받은 JSON 데이터를 파싱
    })
    .then(data => {
        console.log(data);
        // 유사 답변을 마크다운으로 변환하고 HTML로 렌더링합니다.
        const answerMarkdown = data.similarAnswer.replace(/\\"/g, '`');
        const answerHtml = marked.parse(answerMarkdown);

        // 유사 답변 데이터를 기반으로 HTML 요소를 생성하고 컨테이너에 추가
        const similarAnswerItem = document.createElement('li');
        similarAnswerItem.classList.add('message', 'received');
        similarAnswerItem.innerHTML = `
        <div class="message-item message-receiver">
            <div class="message-content">
                <b>Dr.RC</b>
                <div class="message-line"></div>
                <div class="message-text">${answerHtml}
                </div>
            </div>
            <div class="message-line"></div>
            <div class="similar-answers-section"></div>
        </div>`;
        // 유사 답변 내용을 HTML로 설정
        hideLoader(); // 작업 완료 후 로더 숨김
        messageItem.insertAdjacentElement('afterend', similarAnswerItem);
        enableSubmitButton(); // 데이터 처리 완료 후 버튼 활성화
    });
}


// 사용자 대화 내용 출력
document.addEventListener('DOMContentLoaded', function() {
        showLoader(); // 비동기 작업 시작 전 로더 표시
        fetch('/api/get_user_chats/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            data.chats.forEach(chat => {
                const questionMarkdown = chat.question.replace(/\\"/g, '`');
                const answerMarkdown = chat.answer.replace(/\\"/g, '`');

                // 마크다운을 HTML로 변환
                const questionHtml = marked.parse(questionMarkdown);
                const answerHtml = marked.parse(answerMarkdown);

                // 질문 메시지 생성
                const questionItem = document.createElement('li');
                questionItem.classList.add('message', 'sent'); // 'sent' 클래스로 사용자 메시지 스타일 적용
                questionItem.innerHTML = `
                    <div class="message-item message-sender">
                        <div class="message-content">
                            <b>${chat.username}</b>
                            <div class="message-line"></div>
                            <div class="message-text">
                                ${questionHtml}
                            </div>
                        </div>
                    </div>
                `;
                messagesList.appendChild(questionItem);

                // 답변 메시지 생성
                const answerItem = document.createElement('li');
                answerItem.classList.add('message', 'received'); // 'received' 클래스로 Dr.RC 메시지 스타일 적용
                answerItem.innerHTML = `
                <div class="message-item message-receiver">
                    <div class="message-content">
                        <b>Dr.RC</b>
                        <div class="message-line"></div>
                        <div class="message-text">${answerHtml}</div>
                        <div class="message-line"></div>
                        <div class="similar-answers-section"></div>
                    </div>
                </div>`;
                hideLoader(); // 작업 완료 후 로더 숨김
                messagesList.appendChild(answerItem);
                addSimilarAnswersButton(answerItem, chat.id); // 답변에 대한 유사 답변 버튼 추가
                scrollToBottom();
                enableSubmitButton(); // 데이터 처리 완료 후 버튼 활성화
            });
        })
        .catch(error => console.error('Error:', error));
        hideLoader(); // 작업 완료 후 로더 숨김
});


// 쿠키 수집 함수
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById("message_input").addEventListener("keydown", function(event) {
    // Shift + Enter가 눌렸을 때는 줄 바꿈
    if (event.key === "Enter" && event.shiftKey) {
        event.preventDefault(); // 기본 동작을 막음
        var textarea = event.target;
        textarea.value += "\n"; // 새 줄로 이동
    }
    // Enter만 눌렸을 때는 폼 제출
    else if (event.key === "Enter") {
        event.preventDefault(); // 폼이 자동으로 제출되는 것을 방지
        // 폼 제출 로직을 여기에 구현
        var form = document.querySelector('.message-form'); // 폼 선택자에 맞게 조정
        if(form) {
            form.submit(); // 폼 제출
        }
    }
});

