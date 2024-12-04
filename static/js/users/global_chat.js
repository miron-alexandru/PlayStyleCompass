document.addEventListener("DOMContentLoaded", function () {
  const globalChatContainer = document.getElementById('global-chat-container');
  const profileUrlTemplate = globalChatContainer.getAttribute('data-profile-url-template');

  function generateProfileUrl(profileName) {
    return profileUrlTemplate.replace('PROFILE_NAME_PLACEHOLDER', encodeURIComponent(profileName));
  }

  const form = document.getElementById("global-chat-form");
  const inputField = document.getElementById("global-chat-message-input");
  const chatMessages = document.getElementById("global-chat-messages");
  const sseData = document.getElementById("global-sse-data");

  function startSSE(url) {
    const eventSource = new EventSource(url);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const formattedTimestamp = formatTimestamp(data.created_at);

      const messageHTML = `
        <div class="global-message-wrapper" data-message-id="${data.id}">
          <img src="${data.profile_picture_url}" alt="Profile Picture" class="global-chat-profile-picture">
          <div class="message-user-name">
            <a href="${generateProfileUrl(data.profile_name)}" target="_blank">${data.profile_name}</a>
          </div>
          <div class="global-message-box">
            <div class="global-message-content-wrapper">
              <div class="global-message-content">${wrapUrlsWithAnchorTags(data.content)}</div>
              <div class="message-timestamp">${formattedTimestamp}</div>
            </div>
          </div>
        </div>`;

      chatMessages.innerHTML += messageHTML;
      scrollToBottomGlobal();
    };
  }

  startSSE(sseData.getAttribute("data-stream-url"));
});


function scrollToBottomGlobal() {
  const messagesContainer = document.getElementById("global-chat-messages");
  messagesContainer.scrollTo({ top: messagesContainer.scrollHeight, behavior: 'smooth' });
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
  const sendButton = form.querySelector(".global-send-button");

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
  const emojiButton = document.getElementById("global-emoji-button");
  const emojiPickerContainer = document.getElementById("global-emoji-picker");
  const textarea = document.getElementById("global-chat-message-input");

  const picker = new EmojiMart.Picker({
    onEmojiSelect: (emoji) => {
      textarea.value += emoji.native;
      textarea.dispatchEvent(new Event("input"));
      textarea.focus();
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
      scrollToBottomGlobal();
    } else {
      chatContainer.style.display = "none";
    }
  });
});


document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("global-chat-form");
  const textarea = form.querySelector("textarea");
  const submitButton = form.querySelector(".global-send-button");

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