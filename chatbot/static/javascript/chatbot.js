const messagesList = document.querySelector('.messages-list');
const messageForm = document.querySelector('.message-form');
const messageInput = document.querySelector('.message-input');

// upon submission of send button...
messageForm.addEventListener('submit', (event)=> {
    event.preventDefault() // prevent refresh of page on click
    const message = messageInput.value.trim();
    if (message.length === 0){
    return;
    }

    const messageItem = document.createElement('li');
    const messageMarkdown = message.replace(/\\"/g, '`');
    const messageHtml = marked.parse(messageMarkdown);
    messageItem.classList.add('message','sent');
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

    //clear from input box  
    messageInput.value = '';

    //send data to backend
    fetch('/ask_question/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
        'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        'text': message
    })
    })
    .then(response => response.json())
    .then(data => {
        const responseText = data.data; 
        const questionId = data.questionId;
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
            <div class="similar-answers-section">
                <button class="show-similar-answers btn btn-secondary" data-question-id="${questionId}">유사 답변 보기</button>
                <div class="similar-answers-list" style="display:none;" id="similar-answers-list-${questionId}"></div>
            </div>
        </div>
        `;
        messagesList.appendChild(messageItem);
    });

    // 입력 필드 초기화
    messageInput.value = '';
});

// 유사 답변 보기 버튼에 대한 이벤트 리스너를 동적으로 추가
document.addEventListener('DOMContentLoaded', function() {
    // 유사 답변 보기 버튼 클릭 이벤트 처리
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('show-similar-answers')) {
            const questionId = e.target.getAttribute('data-question-id');
            showSimilarAnswers(questionId);
        }
    });
});

function showSimilarAnswers(questionId) {
    // 유사 답변 데이터를 요청하는 URL. 실제 구현에서는 서버 구성에 맞게 조정해야 합니다.
    const url = `/similar-answers/${questionId}/`;
    
    fetch(url, {
        method: 'GET', // 데이터 요청을 위해 GET 메소드 사용
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
        // 유사 답변을 표시할 리스트의 컨테이너 요소를 찾습니다.
        const similarAnswersList = document.getElementById(`similar-answers-list-${questionId}`);
        
        // 기존에 표시된 유사 답변이 있다면 초기화
        similarAnswersList.innerHTML = '';
        
        // 받은 유사 답변 데이터를 기반으로 HTML 요소를 생성하고 컨테이너에 추가
        data.similarAnswers.forEach(answer => {
            const answerElement = document.createElement('div');
            answerElement.classList.add('similar-answer');
            answerElement.textContent = answer; // 유사 답변 내용을 텍스트로 설정
            similarAnswersList.appendChild(answerElement);
        });

        // 유사 답변 리스트를 사용자에게 표시
        similarAnswersList.style.display = 'block';
    })
    .catch(error => {
        console.error('Error fetching similar answers:', error);
        // 오류 처리 로직을 추가할 수 있습니다.
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


function showSimilarAnswers(questionId) {
    fetch(`/similar-answers/${questionId}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const similarAnswersList = document.getElementById(`similar-answers-list-${questionId}`); // 유사 답변을 표시할 요소의 ID를 질문 ID와 연결
        similarAnswersList.innerHTML = ''; // 기존 내용 초기화
        data.similarAnswers.forEach(answer => {
            const answerElement = document.createElement('div');
            answerElement.classList.add('similar-answer');
            answerElement.innerHTML = answer; // 유사 답변 내용
            similarAnswersList.appendChild(answerElement);
        });
        similarAnswersList.style.display = 'block'; // 유사 답변 리스트 표시
    })
    .catch(error => console.error('Error:', error));
}