const chatContainer = document.getElementById("chat-container");
const recipientId = Number(chatContainer.dataset.recipientId);
const userId = Number(chatContainer.dataset.userId);

const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const chatSocket = new WebSocket(
  `${protocol}://${window.location.host}/ws/chat/${recipientId}/`
);

const chatInput = document.getElementById("chat-message-input");
const typingIndicator = document.getElementById("typing-indicator");

let typingTimeout;
let isTyping = false;

const sendTypingStatus = (isTyping) => {
  chatSocket.send(JSON.stringify({ typing: isTyping }));
};

chatInput.addEventListener("input", () => {
  if (!isTyping) {
    isTyping = true;
    sendTypingStatus(true);
  }
  clearTimeout(typingTimeout);
  typingTimeout = setTimeout(() => {
    isTyping = false;
    sendTypingStatus(false);
  }, 2500);
});

chatSocket.onmessage = (e) => {
  const data = JSON.parse(e.data);

  if (data.sender_id !== userId) {
    typingIndicator.style.display = data.typing ? "block" : "none";

    if (data.message_id && data.new_content) {
      const messageElement = document.querySelector(
        `div[data-message-id='${data.message_id}']`
      );
      if (messageElement) {
        const contentElement = messageElement.querySelector(".message-content");
        contentElement.innerHTML = wrapEditedContentWithAnchorTags(
          data.new_content
        );

        let editedIndicator = messageElement.querySelector(".message-edited");
        if (!editedIndicator) {
          editedIndicator = document.createElement("div");
          editedIndicator.classList.add("message-edited");
          editedIndicator.innerText = "Edited";
          contentElement.insertAdjacentElement("afterend", editedIndicator);
        } else {
          editedIndicator.style.display = "block";
        }
      }
    }
  }
};
