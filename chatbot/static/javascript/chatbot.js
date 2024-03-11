const messagesList = document.querySelector('.messages-list');
messagesList.scrollTo(0, messagesList.scrollHeight);
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

        // 유사 답변 보기 버튼에 대한 이벤트 리스너를 직접 추가
        similarAnswersButton.addEventListener('click', function() {
            showSimilarAnswers(questionId);
        });

        // 버튼을 similar-answers-section 내에 추가
        similarAnswersSection.appendChild(similarAnswersButton);
        messagesList.appendChild(messageItem);
    });

    // 입력 필드 초기화
    messageInput.value = '';
});

function showSimilarAnswers(questionId) {
    console.log("showSimilarAnswers called with", questionId)
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
        console.log(data)
        // 질문과 답변을 가져옵니다.
        const similarQuestion = data.similarQuestion; 
        const similarAnswer = data.similarAnswer;

        // 질문과 답변을 마크다운으로 변환하고 HTML로 렌더링합니다.
        const questionMarkdown = similarQuestion.replace(/\\"/g, '`');
        const answerMarkdown = similarAnswer.replace(/\\"/g, '`');
        const questionHtml = marked.parse(questionMarkdown);
        const answerHtml = marked.parse(answerMarkdown);

        // 받은 유사 답변 데이터를 기반으로 HTML 요소를 생성하고 컨테이너에 추가
        const similarAnswerItem = document.createElement('li');
        similarAnswerItem.classList.add('message', 'received');
        similarAnswerItem.innerHTML = `
        <div class="message-text">
            <div class="message-sender">
                <b>Dr.RC</b>
            </div>
            <div class="message-content">
                <strong>유사 질문:</strong> ${questionHtml}
                <strong>답변:</strong> ${answerHtml}
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
