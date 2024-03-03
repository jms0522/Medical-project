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
    messageItem.classList.add('message','sent');
    messageItem.innerHTML = ` 
        <div class="message-text">
        <div class="message-sender">
            <b>You</b>
        </div>
        <div class="message-content">
            ${message}
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
        const messageItem = document.createElement('li');
        messageItem.classList.add('message', 'received');
        messageItem.innerHTML = `
        <div class="message-text">
            <div class="message-sender">
                <b>Dr.RC</b>
            </div>
            <div class="message-content">
                ${responseText}
            </div>
        </div>
        `;
        messagesList.appendChild(messageItem);
    });
});

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
            const questionItem = document.createElement('li');
            questionItem.classList.add('message', 'sent'); // 'sent' 클래스로 사용자 메시지 스타일 적용
            questionItem.innerHTML = `
                <div class="message-text">
                    <div class="message-sender">
                        <b>You</b>
                    </div>
                    <div class="message-content">
                        ${chat.question}
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
                        ${chat.answer}
                    </div>
                </div>
            `;
            messagesList.appendChild(answerItem);
        });
    })
    .catch(error => console.error('Error:', error));
});
