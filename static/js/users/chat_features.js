function scrollToBottom() {
    const chatMessages = document.querySelector('.chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

document.addEventListener('DOMContentLoaded', () => {
    const emojiButton = document.getElementById('emoji-button');
    const emojiPickerContainer = document.getElementById('emoji-picker');
    const textarea = document.getElementById('chat-message-input');

    const picker = new EmojiMart.Picker({
        onEmojiSelect: (emoji) => {
            const editTextarea = document.getElementById('edit-textarea');
            const targetTextarea = editTextarea || textarea;

            targetTextarea.value += emoji.native;
            targetTextarea.dispatchEvent(new Event('input'));
            targetTextarea.focus();
        },
        emojiSize: 24,
        perLine: 8,
    });

    emojiPickerContainer.innerHTML = '';
    emojiPickerContainer.appendChild(picker);

    emojiButton.addEventListener('click', () => {
        emojiPickerContainer.classList.toggle('visible');
    });

    document.addEventListener('click', (event) => {
        if (!emojiPickerContainer.contains(event.target) && !emojiButton.contains(event.target)) {
            emojiPickerContainer.classList.remove('visible');
        }
    });
});



document.addEventListener('DOMContentLoaded', function() {

    const searchButton = document.getElementById('search-messages-button');
    const searchContainer = document.getElementById('search-container');

    function toggleSearchBox() {
        if (searchContainer.style.display === 'none' || searchContainer.style.display === '') {
            searchContainer.style.display = 'block';
            searchInput.focus();
        } else {
            searchContainer.style.display = 'none';
        }
    }

    searchButton.addEventListener('click', toggleSearchBox);

    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function() {
        const query = searchInput.value.toLowerCase();
        filterMessages(query);
    });

    function filterMessages(query) {
        const messages = document.querySelectorAll('.message-wrapper');
        messages.forEach(message => {
            const messageContent = message.querySelector('.message-content').innerText.toLowerCase();
            if (messageContent.includes(query)) {
                message.style.display = '';
            } else {
                message.style.display = 'none';
            }
        });
    }
});


document.addEventListener('DOMContentLoaded', function() {
    const defaultColor = '#e6f7ff';
    const chatMessages = document.querySelector('.chat-messages');
    const form = document.querySelector('form');
    const chatContainer = document.querySelector('.chat-container');
    const changeBgColorButton = document.getElementById('change-bg-color-button');
    const colorPickerContainer = document.getElementById('color-picker-container');
    const defaultColorButton = document.getElementById('default-color-button');

    const pickr = Pickr.create({
        el: '#color-picker',
        theme: 'classic',
        swatches: [
            defaultColor,
            '#ff0000', '#00ff00', '#0000ff',
        ],
        components: {
            preview: true,
            opacity: true,
            hue: true,
            interaction: {
                hex: true,
                rgba: true,
                input: true,
                clear: true,
                save: true
            }
        },
        default: defaultColor,
    });

    changeBgColorButton.addEventListener('click', function() {
        const isDisplayed = colorPickerContainer.style.display === 'flex';
        colorPickerContainer.style.display = isDisplayed ? 'none' : 'flex';
    });

    pickr.on('change', (color) => {
        const selectedColor = color.toHEXA().toString();
        chatMessages.style.backgroundColor = selectedColor;
        form.style.backgroundColor = selectedColor;
        chatContainer.style.backgroundColor = selectedColor;

        localStorage.setItem('chatBackgroundColor', selectedColor);
    });

    defaultColorButton.addEventListener('click', function() {
        pickr.setColor(defaultColor);
        chatMessages.style.backgroundColor = defaultColor;
        form.style.backgroundColor = defaultColor;
        chatContainer.style.backgroundColor = defaultColor;

        localStorage.setItem('chatBackgroundColor', defaultColor);
    });

    const savedColor = localStorage.getItem('chatBackgroundColor');
    if (savedColor) {
        pickr.setColor(savedColor);
        chatMessages.style.backgroundColor = savedColor;
        form.style.backgroundColor = savedColor;
        chatContainer.style.backgroundColor = savedColor;
    }

    document.addEventListener('click', function(event) {
        const pickrApp = document.querySelector('.pcr-app');
        const isColorPickerContainerDisplayed = window.getComputedStyle(colorPickerContainer).display === 'flex';
        const isColorPickerContainerClicked = colorPickerContainer.contains(event.target);
        const isPickrAppClicked = pickrApp && pickrApp.contains(event.target);
        const isChangeBgColorButtonClicked = changeBgColorButton.contains(event.target);

        if (isColorPickerContainerDisplayed &&
            !isColorPickerContainerClicked &&
            !isPickrAppClicked &&
            !isChangeBgColorButtonClicked) {
            colorPickerContainer.style.display = 'none';
        }
    });
});



document.addEventListener('DOMContentLoaded', () => {
    const fileButton = document.getElementById('file-button');
    const fileInput = document.getElementById('file-input');
    const form = document.getElementById('myForm');
    const sendButton = document.querySelector('.send-button');
    const messageTextarea = document.getElementById('chat-message-input');
    const fileIndicator = document.getElementById('file-indicator');

    if (!fileButton || !fileInput || !form || !sendButton || !messageTextarea || !fileIndicator) {
        return;
    }

    fileButton.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        const hasFile = fileInput.files.length > 0;
        const hasMessage = messageTextarea.value.trim();
        const file = hasFile ? fileInput.files[0] : null;
        const fileName = file ? file.name : '';
        const fileSize = file ? formatFileSize(file.size) : '';

        sendButton.disabled = !hasMessage && !hasFile;

        if (hasFile && !hasMessage) {
            sendButton.click();
        }

        if (hasFile) {
            const translatedText = translate('File attached: ');
            fileIndicator.textContent = `${translatedText}${fileName} (${fileSize})`;
            fileIndicator.style.display = 'inline';
        } else {
            fileIndicator.style.display = 'none';
        }
    });

    function formatFileSize(sizeInBytes) {
        if (sizeInBytes < 1024) {
            return `${sizeInBytes} B`;
        } else if (sizeInBytes < 1048576) {
            return `${(sizeInBytes / 1024).toFixed(2)} KB`;
        } else if (sizeInBytes < 1073741824) {
            return `${(sizeInBytes / 1048576).toFixed(2)} MB`;
        } else {
            return `${(sizeInBytes / 1073741824).toFixed(2)} GB`;
        }
    }
});



function getFileNameFromUrl(url) {
        const decodedUrl = decodeURIComponent(url);
        return decodedUrl.substring(decodedUrl.lastIndexOf('/') + 1);
    }

document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', (event) => {
        if (event.target.classList.contains('file-link')) {
            event.preventDefault();
            const fileUrl = event.target.href;
            const fileName = getFileNameFromUrl(fileUrl);
            const translatedText = translate('This file was shared by another user. Do you trust this source and want to download: ');

            if (confirm(`${translatedText}"${fileName}" ?`)) {
                const downloadLink = document.createElement('a');
                downloadLink.href = fileUrl;
                downloadLink.download = fileName;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
            }
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const blockToggleButton = document.getElementById('block-toggle-button');
    const blockUrl = blockToggleButton.getAttribute('data-block-url');
    const unblockUrl = blockToggleButton.getAttribute('data-unblock-url');
    const checkUrl = blockToggleButton.getAttribute('data-check-url');

    const chatContainer = document.getElementById('chat-container');
    const recipientId = Number(chatContainer.dataset.recipientId);
    const userId = Number(chatContainer.dataset.userId);
    const chatMessagesContainer = document.getElementById('chat-messages');

    function updateBlockButton() {
        fetch(checkUrl)
            .then(response => response.json())
            .then(data => {
                if (data.is_blocked) {
                    blockToggleButton.textContent = translate("Unblock");
                    blockToggleButton.onclick = () => unblockUser();
                    addBlockedMessage();
                } else {
                    blockToggleButton.textContent = translate("Block");
                    blockToggleButton.onclick = () => blockUser();
                    removeBlockedMessage();
                }
            });
    }

    updateBlockButton();

    function blockUser() {
        fetch(blockUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            updateBlockButton();
        });
    }

    function unblockUser() {
        fetch(unblockUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            updateBlockButton();
        });
    }

    function addBlockedMessage() {
        const blockedMessage = document.createElement('div');
        blockedMessage.className = 'blocked-message';
        blockedMessage.textContent = translate('User blocked');
        if (!chatMessagesContainer.querySelector('.blocked-message')) {
            chatMessagesContainer.appendChild(blockedMessage);
            scrollToBottom();
        }
    }

    function removeBlockedMessage() {
        const blockedMessage = chatMessagesContainer.querySelector('.blocked-message');
        if (blockedMessage) {
            chatMessagesContainer.removeChild(blockedMessage);
        }
    }
});
