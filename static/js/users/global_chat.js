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
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' }) + 
    ' ' + 
    date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: true });
}

fetch(authCheckUrl)
  .then((response) => response.json())
  .then((data) => {
    if (data.authenticated) {
      const globalChatContainer = document.getElementById('global-chat-container');
      const globalChat_ProfileUrlTemplate = globalChatContainer.getAttribute('data-profile-url-template');
      const errorMessageElement = document.querySelector(".global-error-message p");

      const chatState = localStorage.getItem('chatState') || 'closed';
        if (chatState === 'open') {
          globalChatContainer.style.display = 'flex';
        } else {
          globalChatContainer.style.display = 'none';
        }

      function globalChat_generateProfileUrl(profileName) {
        return globalChat_ProfileUrlTemplate.replace('PROFILE_NAME_PLACEHOLDER', encodeURIComponent(profileName));
      }

      const globalChat_Messages = document.getElementById("global-chat-messages");
      const loadMoreButton = document.getElementById("load-more-messages");
      const getMessagesUrl = globalChatContainer.getAttribute('data-get-messages');
      let currentOffset = 20;
      let allMessagesLoaded = false;

      globalChat_Messages.addEventListener('scroll', function () {
        if (globalChat_Messages.scrollTop === 0 && !allMessagesLoaded) {
          loadMoreButton.style.display = 'block';
        } else {
          loadMoreButton.style.display = 'none';
        }
      });

      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const socket = new WebSocket(`${protocol}://${window.location.host}/ws/global_chat/`);

      socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        const formattedTimestamp = globalChat_formatTimestamp(data.created_at);

        const messageHTML = `
          <div class="global-message-wrapper" data-message-id="${data.id}">
            <img src="${data.profile_picture_url}" alt="Profile Picture" class="global-chat-profile-picture">
            <div class="message-user-name">
              <a href="${globalChat_generateProfileUrl(data.sender_name)}" target="_blank">${data.sender_name}</a>
            </div>
            <div class="global-message-box">
              <div class="global-message-content-wrapper">
                <div class="global-message-content">${globalChat_wrapUrlsWithAnchorTags(data.message)}</div>
                <div class="global-message-timestamp">${formattedTimestamp}</div>
              </div>
            </div>
          </div>`;

        globalChat_Messages.innerHTML += messageHTML;
        globalChat_scrollToBottom();
      };

      loadMoreButton.addEventListener('click', function() {
        loadMessages(currentOffset, 40);
        currentOffset += 40;
      });

      function loadMessages(offset, limit) {
        let messagesLoaded = false;

        fetch(`${getMessagesUrl}?offset=${offset}&limit=${limit}`)
        .then(response => response.json())
        .then(messages => {
            if (messages.length === 0) {
              allMessagesLoaded = true;
              loadMoreButton.style.display = 'none';
              return;
            }

            messages.forEach(message => {
              const formattedTimestamp = globalChat_formatTimestamp(message.created_at);

              const messageHTML = `
                <div class="global-message-wrapper" data-message-id="${message.id}">
                  <img src="${message.profile_picture_url}" alt="Profile Picture" class="global-chat-profile-picture">
                  <div class="message-user-name">
                    <a href="${globalChat_generateProfileUrl(message.sender_name)}" target="_blank">${message.sender_name}</a>
                  </div>
                  <div class="global-message-box">
                    <div class="global-message-content-wrapper">
                      <div class="global-message-content">${globalChat_wrapUrlsWithAnchorTags(message.message)}</div>
                      <div class="global-message-timestamp">${formattedTimestamp}</div>
                    </div>
                  </div>
                </div>`;

               globalChat_Messages.innerHTML = messageHTML + globalChat_Messages.innerHTML;
            });
            messagesLoaded = true;
        })
        .catch(error => console.error('Error loading messages:', error));
    }

      function sendMessage(messageContent) {
        const messageData = { message: messageContent };
        socket.send(JSON.stringify(messageData));
      }

      function createMessage(messageContent) {
        const form = document.getElementById("global-chat-form");
        const endpointUrl = form.dataset.url;
        const sendButton = form.querySelector(".global-send-button");
        const textarea = form.querySelector("textarea");

        const formData = new FormData();
        formData.append("content", messageContent);

        fetch(endpointUrl, {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': csrfToken,
          },
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'Message created') {
            textarea.focus();
            textarea.value = ""; 
            updateSendButtonState();
          } else {
            console.error('Error creating message:', data.error);

            if (data.rate_limited) {
              disableInputAndButton();
              showCooldownMessage();
              startCooldown(15);
            }
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
      }

      function updateSendButtonState() {
        const textarea = document.getElementById("global-input");
        const sendButton = document.querySelector(".global-send-button");
        sendButton.disabled = !textarea.value.trim();
      }

      function disableInputAndButton() {
        const textarea = document.getElementById("global-input");
        const sendButton = document.querySelector(".global-send-button");
        textarea.disabled = true;
        sendButton.disabled = true;
      }

      function enableInputAndButton() {
        const textarea = document.getElementById("global-input");
        const sendButton = document.querySelector(".global-send-button");
        textarea.disabled = false;
        sendButton.disabled = !textarea.value.trim();
      }

      function showCooldownMessage() {
        errorMessageElement.style.display = "block"; 
        errorMessageElement.textContent = "You are sending messages too quickly. Please wait 15 seconds.";
      }

      function hideCooldownMessage() {
        errorMessageElement.style.display = "none";
      }

      function startCooldown(seconds) {
        let remainingTime = seconds;

        const countdownInterval = setInterval(function () {
          errorMessageElement.textContent = `You are sending messages too quickly. Please wait ${remainingTime} seconds.`;
          remainingTime--;

          if (remainingTime < 0) {
            clearInterval(countdownInterval);
            enableInputAndButton();
            hideCooldownMessage();
          }
        }, 1000);
      }

      document.getElementById("global-input").addEventListener("input", function () {
        updateSendButtonState();
      });

      document.getElementById("global-chat-form").addEventListener("submit", function (event) {
        event.preventDefault();
        const textarea = document.getElementById("global-input");
        const messageContent = textarea.value.trim();

        if (messageContent) {
          createMessage(messageContent);
          sendMessage(messageContent);
        }
      });

      updateSendButtonState();
    }
  })
  .catch((error) => console.error("Error:", error));



fetch(authCheckUrl)
  .then((response) => response.json())
  .then((data) => {
    if (data.authenticated) {
      const initializeGlobalChat = () => {
        // Emoji Picker
        const globalChat_EmojiButton = document.getElementById("global-emoji-button");
        const globalChat_EmojiPickerContainer = document.getElementById("global-emoji-picker");
        const globalChat_Textarea = document.getElementById("global-input");

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

        // Chat Toggle
        const globalChat_ToggleButton = document.getElementById("toggle-chat-button");
        const globalChat_Container = document.getElementById("global-chat-container");

        globalChat_ToggleButton.addEventListener("click", () => {
          if (globalChat_Container.style.display === "none") {
            globalChat_Container.style.display = "flex";
            globalChat_scrollToBottom();
            localStorage.setItem('chatState', 'open');
          } else {
            globalChat_Container.style.display = "none";
            localStorage.setItem('chatState', 'closed');
          }
        });

        // Submit Messages on Enter
        const globalChat_Form = document.getElementById("global-chat-form");
        const globalChat_SubmitButton = globalChat_Form.querySelector(".global-send-button");

        globalChat_Textarea.addEventListener("keydown", (event) => {
          if (
            event.keyCode === 13 &&
            !event.shiftKey &&
            globalChat_Textarea.value.trim() !== ""
          ) {
            event.preventDefault();
            globalChat_SubmitButton.click();
          }
        });
      };

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeGlobalChat);
      } else {
        initializeGlobalChat();
      }
    }
  })
  .catch((error) => console.error("Error:", error));
