let eventSource;

document.addEventListener('DOMContentLoaded', function() {
    const sseData = document.getElementById('sse-data');
    const noMessagesText = translate("No messages. Say something!");

    function startSSE(url) {
        eventSource = new EventSource(url);
        eventSource.onmessage = event => {
            const data = JSON.parse(event.data);
            const messageHTML = `
                    <div class="message-box">
                        <div class="message-author">${data.sender__userprofile__profile_name}</div>
                        <div class="message-content">${wrapUrlsWithAnchorTags(data.content)}</div>
                    </div>`;
            sseData.innerHTML += messageHTML;
            scrollToBottom();
            checkForMessages();
        };
    }

    function wrapUrlsWithAnchorTags(content) {
        return content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
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
    document.getElementById('clear-chat-button').addEventListener('click', function() {
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
    });
});