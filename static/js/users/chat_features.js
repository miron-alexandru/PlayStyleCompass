document.addEventListener('DOMContentLoaded', () => {
    const emojiButton = document.getElementById('emoji-button');
    const emojiPickerContainer = document.getElementById('emoji-picker');
    const textarea = document.getElementById('chat-message-input');

    const picker = new EmojiMart.Picker({
        onEmojiSelect: (emoji) => {
            textarea.value += emoji.native;
            textarea.dispatchEvent(new Event('input'));
            textarea.focus();
        },
        emojiSize: 24,
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
    default: '#e6f7ff', 
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
        if (colorPickerContainer.style.display === 'flex' &&
            !colorPickerContainer.contains(event.target) &&
            !changeBgColorButton.contains(event.target)) {
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

    if (!fileButton || !fileInput || !form || !sendButton || !messageTextarea) {
        return;
    }

    fileButton.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        sendButton.disabled = !messageTextarea.value.trim() && !fileInput.files.length;

        if (fileInput.files.length > 0) {
            sendButton.click();
        }
    });
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

            if (confirm(`This file was shared by another user. Do you trust this source and want to download: "${fileName}" ?`)) {
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