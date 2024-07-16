let eventSource;

function confirmVisit(url) {
        const translatedText = translate("Are you sure you want to visit this website?\n\n");
        return confirm(`${translatedText}${url}`);
    }

function wrapEditedContentWithAnchorTags(content) {
    const urlRegex = /(https?:\/\/[^\s]+)/g;

    return content.replace(urlRegex, (url) => {
        return `<a href="${url}" onclick="return confirmVisit('${url}')" target="_blank">${url}</a>`;
    });
}

function editMessage(messageId) {
    const messageElement = document.querySelector(`div[data-message-id='${messageId}']`);
    const contentElement = messageElement.querySelector('.message-content');
    const originalContent = contentElement.innerText;
    const messagesContainer = document.getElementById('chat-messages');
    const editUrlTemplate = messagesContainer.getAttribute('data-edit-message-url');
    const editUrl = editUrlTemplate.replace('/0/', `/${messageId}/`);

    const input = messageElement.querySelector('textarea');
    if (input) {
        return;
    }

    const inputField = document.createElement('textarea');
    inputField.value = originalContent;
    inputField.classList.add('edit-textarea');
    inputField.placeholder = 'Edit your message...';
    contentElement.replaceWith(inputField);

    const saveButton = document.createElement('button');
    saveButton.innerText = 'Save';
    saveButton.classList.add('save-message-button');
    messageElement.querySelector('.message-content-wrapper').appendChild(saveButton);

    const editButton = messageElement.querySelector('.edit-message-button');
    if (editButton) {
        editButton.style.display = 'none';
    }

    saveButton.addEventListener('click', () => {
        const newContent = inputField.value;

        fetch(editUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
            },
            body: new URLSearchParams({ content: newContent }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Message updated') {
                inputField.replaceWith(contentElement);
                contentElement.innerHTML = wrapEditedContentWithAnchorTags(newContent);
                saveButton.remove();

                if (editButton) {
                    editButton.style.display = 'inline-block';
                }
            } else {
                alert(data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    });
}


document.addEventListener('DOMContentLoaded', function() {
    const sseData = document.getElementById('sse-data');
    const noMessagesText = translate("No messages. Say something!");
    const chatContainer = document.getElementById('chat-container');
    const currentUserId = parseInt(chatContainer.getAttribute('data-user-id'));

    function startSSE(url) {
        eventSource = new EventSource(url);
        eventSource.onmessage = event => {
            const data = JSON.parse(event.data);
            const isCurrentUser = data.sender__id === currentUserId;

            const messageHTML = `
            <div class="message-wrapper ${isCurrentUser ? 'sent' : 'received'}" data-message-id="${data.id}">
                <img src="${data.profile_picture_url}" alt="Profile Picture" class="chat-profile-picture">
                <div class="message-box ${isCurrentUser ? 'sent' : 'received'}">
                    <div class="message-content-wrapper" data-creation-time="${data.created_at}">
                        <div class="message-author">${data.sender__userprofile__profile_name}</div>
                        <div class="message-content">${wrapUrlsWithAnchorTags(data.content)}</div>
                        ${isCurrentUser ? (isNewMessage(data.created_at) ? '<button class="edit-message-button">Edit</button>' : '') : ''}
                    </div>
                </div>
            </div>`;

            sseData.innerHTML += messageHTML;
            scrollToBottom();
            checkForMessages();

            const editButtons = document.querySelectorAll('.edit-message-button');
            editButtons.forEach(editButton => {
                editButton.removeEventListener('click', handleEditButtonClick);
                editButton.addEventListener('click', handleEditButtonClick);
            });
        };
    }

    function isNewMessage(created_at) {
        const messageTime = new Date(created_at).getTime();
        const currentTime = new Date().getTime();
        const elapsedTimeInSeconds = (currentTime - messageTime) / 1000;
        return elapsedTimeInSeconds <= 120;
    }

    function handleEditButtonClick(event) {
        const messageId = event.target.closest('.message-wrapper').getAttribute('data-message-id');
        editMessage(messageId);
    }

    setInterval(() => {
        const messageWrappers = document.querySelectorAll('.message-wrapper');
        messageWrappers.forEach(wrapper => {
            const messageId = wrapper.getAttribute('data-message-id');
            const editButton = wrapper.querySelector('.edit-message-button');
            if (editButton) {
                const creationTime = wrapper.querySelector('.message-content-wrapper').getAttribute('data-creation-time');
                if (!isNewMessage(creationTime)) {
                    editButton.style.display = 'none';
                }
            }
        });
    }, 3000);


    function wrapUrlsWithAnchorTags(content) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        
        return content.replace(urlRegex, (url) => {
            return `<a href="${url}" onclick="return confirmVisit('${url}')" target="_blank">${url}</a>`;
        });
    }

    function checkForMessages() {
        if (sseData.children.length === 0) {
            sseData.innerHTML = `<div class="no-messages">${noMessagesText}</div>`;
        } else {
            const noMessagesDiv = document.querySelector('.no-messages');
            if (noMessagesDiv) {
                noMessagesDiv.remove();
            }
        }
    }

    if (typeof(EventSource) !== 'undefined') {
        const streamUrl = sseData.dataset.streamUrl;
        startSSE(streamUrl);
        scrollToBottom();
        checkForMessages();
    } else {
        sseData.innerHTML = 'Your browser doesn\'t receive server-sent events.';
    }
});


function scrollToBottom() {
    const chatMessages = document.querySelector('.chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function submit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const endpointUrl = event.target.dataset.url;
    const textarea = event.target.querySelector('textarea');

    fetch(endpointUrl, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": csrfToken,
        }
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
        if (status === 201) {
            this.state = 'success';
            textarea.focus();
            textarea.value = ''; 
            this.errors = {};
            this.content = '';
        } else {
            this.state = 'error';
            this.errors = { message: body.error || 'Unknown error' };
        }
    })
    .catch(error => {
        console.error('Error:', error);
        this.state = 'error';
        this.errors = { message: 'An error occurred while sending the message.' };
    });
};

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('myForm');
    const textarea = form.querySelector('textarea');
    const submitButton = form.querySelector('.send-button');

    textarea.addEventListener('keydown', function(event) {
        if (event.keyCode === 13 && !event.shiftKey && textarea.value.trim() !== '') {
            event.preventDefault();
            submitButton.click();
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('clear-chat-button').addEventListener('click', function(event) {

        if (confirm(translate("Are you sure you want to delete all messages?"))) {
            const url = this.getAttribute('data-url');
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.querySelector('.chat-messages').innerHTML = '';
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        } else {
            return false;
        }
    });
});

function toggleOptionsMenu() {
    const menu = document.getElementById('options-menu');
    if (menu.style.display === 'block') {
        menu.style.display = 'none';
    } else {
        menu.style.display = 'block';
    }
}

document.addEventListener('click', function (event) {
    const menu = document.getElementById('options-menu');
    if (!menu.contains(event.target) && !event.target.classList.contains('options-button')) {
        menu.style.display = 'none';
    }
});