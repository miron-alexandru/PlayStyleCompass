document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("global-chat-form");
  const inputField = document.getElementById("chat-message-input");
  const chatMessages = document.getElementById("chat-messages");
  const sseData = document.getElementById("sse-data");
  const currentUserId = parseInt(document.getElementById("global-chat-container").getAttribute("data-user-id"));

  function startSSE(url) {
    const eventSource = new EventSource(url);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const isCurrentUser = data.sender__id === currentUserId;
      const formattedTimestamp = formatTimestamp(data.created_at);

      const messageHTML = `
        <div class="message-wrapper" data-message-id="${data.id}">
          <img src="${data.profile_picture_url}" alt="Profile Picture" class="chat-profile-picture">
          <div class="message-profile-name">${data.profile_name}</div>
          <div class="message-box">
            <div class="message-content-wrapper">
              <div class="message-content">${wrapUrlsWithAnchorTags(data.content)}</div>
              <div class="message-timestamp">${formattedTimestamp}</div>
            </div>
          </div>
        </div>`;

      chatMessages.innerHTML += messageHTML;
      scrollToBottom();
    };
  }

  startSSE(sseData.getAttribute("data-stream-url"));
});


function scrollToBottom() {
  const messagesContainer = document.getElementById("chat-messages");
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function wrapUrlsWithAnchorTags(text) {
  const urlPattern = /(\b(https?:\/\/[^\s]+))/g;
  return text.replace(urlPattern, '<a href="$1" target="_blank">$1</a>');
}

function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function submitglobalmessage(event) {
  event.preventDefault();

  const form = event.target;
  const formData = new FormData(form);
  const endpointUrl = form.dataset.url;
  const textarea = form.querySelector("textarea");
  const sendButton = form.querySelector(".send-button");

  fetch(endpointUrl, {
    method: "POST",
    body: formData,
    headers: {
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) =>
      response.json().then((data) => ({ status: response.status, body: data }))
    )
    .then(({ status, body }) => {
      if (status === 201) {
        this.state = "success";
        textarea.focus();
        textarea.value = ""; 
        this.errors = {};
        this.content = "";
        sendButton.disabled = !textarea.value.trim();

      } else {
        this.state = "error";
        this.errors = { message: body.error || "Unknown error" };

        setTimeout(() => {
          this.state = "";
          this.errors = {};
        }, 4000);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      this.state = "error";
      this.errors = { message: "An error occurred while sending the message." };

      setTimeout(() => {
        this.state = "";
        this.errors = {};
      }, 4000);
    });
}


document.addEventListener("DOMContentLoaded", () => {
  const emojiButton = document.getElementById("emoji-button");
  const emojiPickerContainer = document.getElementById("emoji-picker");
  const textarea = document.getElementById("chat-message-input");

  const picker = new EmojiMart.Picker({
    onEmojiSelect: (emoji) => {
      const editTextarea = document.getElementById("edit-textarea");
      const targetTextarea = editTextarea || textarea;

      targetTextarea.value += emoji.native;
      targetTextarea.dispatchEvent(new Event("input"));
      targetTextarea.focus();
    },
    emojiSize: 24,
    perLine: 8,
  });

  emojiPickerContainer.innerHTML = "";
  emojiPickerContainer.appendChild(picker);

  emojiButton.addEventListener("click", () => {
    emojiPickerContainer.classList.toggle("visible");
  });

  document.addEventListener("click", (event) => {
    if (
      !emojiPickerContainer.contains(event.target) &&
      !emojiButton.contains(event.target)
    ) {
      emojiPickerContainer.classList.remove("visible");
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("toggle-chat-button");
  const chatContainer = document.getElementById("global-chat-container");

  toggleButton.addEventListener("click", function () {
    if (chatContainer.style.display === "none") {
      chatContainer.style.display = "flex"; 
    } else {
      chatContainer.style.display = "none";
    }
  });
});


document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("global-chat-form");
  const textarea = form.querySelector("textarea");
  const submitButton = form.querySelector(".send-button");

  textarea.addEventListener("keydown", function (event) {
    if (
      event.keyCode === 13 &&
      !event.shiftKey &&
      textarea.value.trim() !== ""
    ) {
      event.preventDefault();
      submitButton.click();
    }
  });
});