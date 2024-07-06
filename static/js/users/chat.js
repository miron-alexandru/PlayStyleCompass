let eventSource;

document.addEventListener('DOMContentLoaded', function() {
    const sseData = document.getElementById('sse-data');

    function startSSE(url) {
        eventSource = new EventSource(url);
        eventSource.onmessage = event => {
            const data = JSON.parse(event.data);
            const messageHTML = `
                    <div class="message-box">
                        <div class="message-author">${data.sender__userprofile__profile_name}</div>
                        <div class="message-content">${data.content}</div>
                    </div>`;
            sseData.innerHTML += messageHTML;
            scrollToBottom();
        };
    }

    if (typeof(EventSource) !== 'undefined') {
        const streamUrl = sseData.dataset.streamUrl;
        startSSE(streamUrl);
        scrollToBottom();
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
        .then(response => {
            this.state = response.ok ? 'success' : 'error';
            return response.json();
        })
        .then(data => {
            if (this.state === 'success') {
                textarea.value = ''; 
            } else {
                this.errors = data.errors || {};
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.state = 'error';
        });
};
