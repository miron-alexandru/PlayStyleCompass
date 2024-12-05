document.addEventListener("DOMContentLoaded", function () {
  const globalChatContainer = document.getElementById('global-chat-container');
  const globalChat_ProfileUrlTemplate = globalChatContainer.getAttribute('data-profile-url-template');

  function globalChat_generateProfileUrl(profileName) {
    return globalChat_ProfileUrlTemplate.replace('PROFILE_NAME_PLACEHOLDER', encodeURIComponent(profileName));
  }

  const globalChat_Form = document.getElementById("global-chat-form");
  const globalChat_InputField = document.getElementById("global-chat-message-input");
  const globalChat_Messages = document.getElementById("global-chat-messages");
  const globalChat_SSEData = document.getElementById("global-sse-data");

  function globalChat_startSSE(url) {
    const globalChat_EventSource = new EventSource(url);
    globalChat_EventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const formattedTimestamp = globalChat_formatTimestamp(data.created_at);

      const messageHTML = `
        <div class="global-message-wrapper" data-message-id="${data.id}">
          <img src="${data.profile_picture_url}" alt="Profile Picture" class="global-chat-profile-picture">
          <div class="message-user-name">
            <a href="${globalChat_generateProfileUrl(data.profile_name)}" target="_blank">${data.profile_name}</a>
          </div>
          <div class="global-message-box">
            <div class="global-message-content-wrapper">
              <div class="global-message-content">${globalChat_wrapUrlsWithAnchorTags(data.content)}</div>
              <div class="global-message-timestamp">${formattedTimestamp}</div>
            </div>
          </div>
        </div>`;

      globalChat_Messages.innerHTML += messageHTML;
      globalChat_scrollToBottom();
    };
  }

  globalChat_startSSE(globalChat_SSEData.getAttribute("data-stream-url"));
});

function globalChat_scrollToBottom() {
  const messagesContainer = document.getElementById("global-chat-messages");
  messagesContainer.scrollTo({ top: messagesContainer.scrollHeight, behavior: 'smooth' });
}

function globalChat_wrapUrlsWithAnchorTags(text) {
  const urlPattern = /(\b(https?:\/\/[^\s]+))/g;
  return text.replace(urlPattern, '<a href="$1" target="_blank">$1</a>');
}

function globalChat_formatTimestamp(timestamp) {
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
        textarea.focus();
        textarea.value = ""; 
        sendButton.disabled = !textarea.value.trim();
      } else {
        console.error("Message sending error:", body.error || "Unknown error");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const globalChat_EmojiButton = document.getElementById("global-emoji-button");
  const globalChat_EmojiPickerContainer = document.getElementById("global-emoji-picker");
  const globalChat_Textarea = document.getElementById("global-chat-message-input");

  const picker = new EmojiMart.Picker({
    onEmojiSelect: (emoji) => {
      globalChat_Textarea.value += emoji.native;
      globalChat_Textarea.dispatchEvent(new Event("input"));
      globalChat_Textarea.focus();
    },
    emojiSize: 24,
    perLine: 8,
  });

  globalChat_EmojiPickerContainer.innerHTML = "";
  globalChat_EmojiPickerContainer.appendChild(picker);

  globalChat_EmojiButton.addEventListener("click", () => {
    globalChat_EmojiPickerContainer.classList.toggle("visible");
  });

  document.addEventListener("click", (event) => {
    if (
      !globalChat_EmojiPickerContainer.contains(event.target) &&
      !globalChat_EmojiButton.contains(event.target)
    ) {
      globalChat_EmojiPickerContainer.classList.remove("visible");
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const globalChat_ToggleButton = document.getElementById("toggle-chat-button");
  const globalChat_Container = document.getElementById("global-chat-container");

  globalChat_ToggleButton.addEventListener("click", function () {
    if (globalChat_Container.style.display === "none") {
      globalChat_Container.style.display = "flex";
      globalChat_scrollToBottom();
    } else {
      globalChat_Container.style.display = "none";
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const globalChat_Form = document.getElementById("global-chat-form");
  const globalChat_Textarea = globalChat_Form.querySelector("textarea");
  const globalChat_SubmitButton = globalChat_Form.querySelector(".global-send-button");

  globalChat_Textarea.addEventListener("keydown", function (event) {
    if (
      event.keyCode === 13 &&
      !event.shiftKey &&
      globalChat_Textarea.value.trim() !== ""
    ) {
      event.preventDefault();
      globalChat_SubmitButton.click();
    }
  });
});
