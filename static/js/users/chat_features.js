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
