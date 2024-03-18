const messagesList = document.querySelector('.messages-list');
const messageForm = document.querySelector('.message-form');
const messageInput = document.querySelector('.message-input');

document.addEventListener('DOMContentLoaded', function() {
    const messagesList = document.querySelector('.messages-list');
    const messageForm = document.querySelector('.message-form');
    const messageInput = document.querySelector('.message-input');

    if (messagesList) {
        messagesList.scrollTo(0, messagesList.scrollHeight);
    }

    if (messageForm) {
        messageForm.addEventListener('submit', (event) => {
            event.preventDefault(); // 폼의 기본 제출 동작을 방지

            const message = messageInput.value.trim();
            if (message.length === 0) {
                return;
            }

            // 사용자 메시지 화면에 표시
            const messageItem = document.createElement('li');
            const messageMarkdown = message.replace(/\\"/g, '`');
            const messageHtml = marked.parse(messageMarkdown);
            messageItem.classList.add('message', 'sent');
            messageItem.innerHTML = `
                <div class="message-text">
                    <div class="message-sender">
                        <b>You</b>
                    </div>
                    <div class="message-content">
                        ${messageHtml}
                    </div>
                </div>`;
            messagesList.appendChild(messageItem);

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
                    console.error('로그인이 필요합니다.');
                    window.location.href = `/common/login/?message=loginRequired`; // 로그인 페이지로 리다이렉트
                    return;
                }
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(text => {
                try {
                    const data = JSON.parse(text); // JSON 형식인 경우 파싱
                    // 서버로부터의 응답 처리 로직
                    processServerResponse(data);
                } catch (e) {
                    if (text.includes('<!DOCTYPE html>')) {
                        // 응답이 HTML 문서인 경우(로그인 페이지)
                        console.error('Redirected to login page.');
                        window.location.href = '/common/login/'; // 로그인 페이지로 리다이렉트
                    } else {
                        throw e; // 다른 형식의 에러 처리
                    }
                }
            })
            .catch(error => console.error('Fetch error:', error));
            // 입력 필드 초기화
            messageInput.value = '';
        });
    }
});

function processServerResponse(data) {
    const responseText = data.data; 
    const questionId = data.id;
    const responseTextMarkdown = responseText.replace(/\\"/g, '`');
    const responseTextHtml = marked.parse(responseTextMarkdown);
    
    // 답변 항목 생성
    const messageItem = document.createElement('li');
    messageItem.classList.add('message', 'received');
    messageItem.innerHTML = `
    <div class="message-text">
        <div class="message-sender">
            <b>Dr.RC</b>
        </div>
        <div class="message-content">
            ${responseTextHtml}
        </div>
        <div class="similar-answers-section"></div>
    </div>
    `;
    
    // 유사 답변 보기 버튼 생성 및 추가
    const similarAnswersSection = messageItem.querySelector('.similar-answers-section');
    const similarAnswersButton = document.createElement('button');
    similarAnswersButton.textContent = "유사 답변 보기";
    similarAnswersButton.classList.add('show-similar-answers', 'btn', 'btn-secondary');
    similarAnswersButton.setAttribute('data-question-id', questionId);
    similarAnswersButton.setAttribute('name', 'similarAnswersButton');

    // 유사 답변 보기 버튼에 대한 이벤트 리스너를 직접 추가
    similarAnswersButton.addEventListener('click', function() {
        showSimilarAnswers(questionId);
    });

    // 버튼을 similar-answers-section 내에 추가
    similarAnswersSection.appendChild(similarAnswersButton);
    messagesList.appendChild(messageItem);
}

function showSimilarAnswers(questionId) {
    console.log("showSimilarAnswers called with", questionId);
    const url = `/similar-answers/${questionId}/`;

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
        <div class="message-text">
            <div class="message-sender">
                <b>Dr.RC</b>
            </div>
            <div class="message-content">
                ${answerHtml}
            </div>
        </div>
        `; // 유사 답변 내용을 HTML로 설정
        messagesList.appendChild(similarAnswerItem);
    });
}



document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/get_user_chats/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        data.chats.forEach(chat => {
            const questionMarkdown = chat.question.replace(/\\"/g, '`');
            const answerMarkdown = chat.answer.replace(/\\"/g, '`');

            // 마크다운을 HTML로 변환
            const questionHtml = marked.parse(questionMarkdown);
            const answerHtml = marked.parse(answerMarkdown);

            // 질문 메시지 추가
            const questionItem = document.createElement('li');
            questionItem.classList.add('message', 'sent'); // 'sent' 클래스로 사용자 메시지 스타일 적용
            questionItem.innerHTML = `
                <div class="message-text">
                    <div class="message-sender">
                        <b>${chat.username}</b>
                    </div>
                    <div class="message-content">
                        ${questionHtml}
                    </div>
                </div>
            `;
            messagesList.appendChild(questionItem);

            // 답변 메시지 추가
            const answerItem = document.createElement('li');
            answerItem.classList.add('message', 'received'); // 'received' 클래스로 Dr.RC 메시지 스타일 적용
            answerItem.innerHTML = `
                <div class="message-text">
                    <div class="message-sender">
                        <b>Dr.RC</b>
                    </div>
                    <div class="message-content">
                        ${answerHtml}
                    </div>
                </div>
                </div>
            `;
            messagesList.appendChild(answerItem);
        });
    })
    .catch(error => console.error('Error:', error));
});
