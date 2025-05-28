function confirmVisit(url) {
  const translatedText = translate(
    "Are you sure you want to visit this website?\n\n"
  );
  return confirm(`${translatedText}${url}`);
}

function wrapEditedContentWithAnchorTags(content) {
  const urlRegex = /(https?:\/\/[^\s]+)/g;

  return content.replace(urlRegex, (url) => {
    return `<a href="${url}" onclick="return confirmVisit('${url}')" target="_blank">${url}</a>`;
  });
}

function scrollToBottom() {
  const chatMessages = document.querySelector(".chat-messages");
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function toggleOptionsMenu() {
  const menu = document.getElementById("options-menu");
  if (menu.style.display === "block") {
    menu.style.display = "none";
  } else {
    menu.style.display = "block";
  }
}

function isNewMessage(created_at) {
  const messageTime = new Date(created_at).getTime();
  const currentTime = new Date().getTime();
  const elapsedTimeInSeconds = (currentTime - messageTime) / 1000;
  return elapsedTimeInSeconds <= 120;
}

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

function loadPinnedMessages() {
  const pinnedMessagesList = document.getElementById("pinned-messages-list");
  const pinnedMessagesButton = document.getElementById(
    "pinned-messages-button"
  );
  const loadPinnedMessagesUrl = pinnedMessagesButton.getAttribute(
    "data-load-pinned-messages"
  );

  fetch(loadPinnedMessagesUrl)
    .then((response) => response.json())
    .then((pinnedMessages) => {
      pinnedMessagesList.innerHTML = "";

      if (pinnedMessages.length === 0) {
        const li = document.createElement("li");
        li.classList.add("pinned-message-item");
        li.textContent = translate("No pinned messages");
        pinnedMessagesList.appendChild(li);
      } else {
        pinnedMessages.forEach((message) => {
          const li = document.createElement("li");
          li.classList.add("pinned-message-item");
          li.setAttribute("data-message-id", message.id);

          const contentDiv = document.createElement("div");
          contentDiv.classList.add("pinned-message-content");
          contentDiv.textContent = message.content;

          li.appendChild(contentDiv);

          if (message.file) {
            const fileDiv = document.createElement("div");
            fileDiv.classList.add("pinned-message-file");

            const fileLink = document.createElement("a");
            fileLink.href = message.file;
            fileLink.download = getFileNameFromUrl(message.file);
            fileLink.classList.add("file-link");
            fileLink.textContent = getFileNameFromUrl(message.file);

            fileDiv.textContent = `${translate("File Attachment: ")} `;
            fileDiv.appendChild(fileLink);

            if (message.file_size) {
              const fileSizeSpan = document.createElement("span");
              fileSizeSpan.textContent = `  (${formatFileSize(
                message.file_size
              )})`;
              fileDiv.appendChild(fileSizeSpan);
            }

            li.appendChild(fileDiv);
          }

          const senderName = message.sender__userprofile__profile_name;

          const senderDiv = document.createElement("div");
          senderDiv.classList.add("pinned-message-sender");
          senderDiv.textContent = `${translate("Sender")}: ${senderName}`;

          const timestamp = message.created_at
            ? new Date(message.created_at).toLocaleString("default", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                second: undefined,
                hour12: true,
              })
            : translate("Unknown time");

          const timestampDiv = document.createElement("div");
          timestampDiv.classList.add("pinned-message-timestamp");
          timestampDiv.textContent = `${timestamp}`;

          const unpinButton = document.createElement("button");
          unpinButton.classList.add("unpin-message");
          unpinButton.innerHTML = translate("Unpin");
          unpinButton.addEventListener("click", () =>
            togglePinMessage(message.id, unpinButton)
          );

          const jumpButton = document.createElement("button");
          jumpButton.classList.add("jump-to-message");
          jumpButton.innerHTML = translate("Show");
          jumpButton.addEventListener("click", () => {
            const chatMessage = document.querySelector(
              `.message-wrapper[data-message-id="${message.id}"]`
            );

            let existingNotice = document.querySelector(".message-not-found");
            if (existingNotice) {
              existingNotice.remove();
            }

            if (chatMessage) {
              chatMessage.scrollIntoView({
                behavior: "smooth",
                block: "center",
              });
              chatMessage.classList.add("highlighted-message");
              setTimeout(() => {
                chatMessage.classList.remove("highlighted-message");
              }, 2000);
            } else {
              const notice = document.createElement("span");
              notice.classList.add("message-not-found");
              notice.textContent = translate("Message not found");

              contentDiv.insertAdjacentElement("beforeend", notice);

              setTimeout(() => {
                notice.remove();
              }, 2000);
            }
          });

          li.appendChild(senderDiv);
          li.appendChild(timestampDiv);
          li.appendChild(jumpButton);
          li.appendChild(unpinButton);

          pinnedMessagesList.appendChild(li);
        });
      }
    })
    .catch((error) => console.error("Error loading pinned messages:", error));
}

function submit(event) {
  event.preventDefault();

  const form = event.target;
  const formData = new FormData(form);
  const endpointUrl = form.dataset.url;
  const textarea = form.querySelector("textarea");
  const fileInput = form.querySelector('input[type="file"]');
  const sendButton = document.querySelector(".send-button");
  const fileIndicator = document.getElementById("file-indicator");
  const hasFile = fileInput.files.length > 0;

  // Prepare data to send
  const messageData = {
    content: textarea.value.trim(),
    file: null,
    file_size: null,
    message_id: null,
  };

  if (hasFile) {
    const file = fileInput.files[0];
    messageData.file = file;
    messageData.file_size = file.size;
    formData.append("file", file);
  }

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
        fileInput.value = "";
        this.errors = {};
        sendButton.disabled = !textarea.value.trim();

        if (hasFile) {
          fileIndicator.style.display = "none";
        }

        messageData.message_id = body.id;
        messageData.file = body.file;
        messageData.file_size = body.file_size;
        messageData.edited = body.edited;
        messageData.is_pinned = body.is_pinned;

        sendMessage(messageData);
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

function sendMessage({ content, file, file_size, message_id, edited, is_pinned }) {
  const message = {
    message: content,
    file: file,
    file_size: file_size,
    message_id: message_id,
    edited: edited,
    is_pinned: is_pinned,
  };

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  } else {
    console.error("WebSocket connection is not open.");
  }
}


function editMessage(messageId) {
  const messageElement = document.querySelector(
    `div[data-message-id='${messageId}']`
  );
  const contentElement = messageElement.querySelector(".message-content");
  const originalContent = contentElement.innerText;
  const messagesContainer = document.getElementById("chat-messages");
  const editUrlTemplate = messagesContainer.getAttribute(
    "data-edit-message-url"
  );
  const editUrl = editUrlTemplate.replace("/0/", `/${messageId}/`);

  const input = messageElement.querySelector("textarea");
  if (input) {
    return;
  }

  const inputField = document.createElement("textarea");
  inputField.value = originalContent;
  inputField.classList.add("edit-textarea");
  inputField.id = "edit-textarea";
  inputField.placeholder = translate("Edit your message...");
  contentElement.replaceWith(inputField);

  const saveButton = document.createElement("button");
  saveButton.innerText = translate("Save");
  saveButton.classList.add("save-message-button");
  const cancelButton = document.createElement("button");
  cancelButton.innerText = translate("Cancel");
  cancelButton.classList.add("cancel-message-button");

  const buttonWrapper = messageElement.querySelector(
    ".message-content-wrapper"
  );
  buttonWrapper.appendChild(saveButton);
  buttonWrapper.appendChild(cancelButton);

  const editButton = messageElement.querySelector(".edit-message-button");
  const pinButton = messageElement.querySelector(".pin-message-button");
  editButton.style.display = "none";
  pinButton.style.display = "none";

  function cancelEdit() {
    inputField.replaceWith(contentElement);
    contentElement.innerText = originalContent;
    saveButton.remove();
    cancelButton.remove();
    editButton.style.display = "";
    pinButton.style.display = "";
  }

  let isTextareaOpened = true;

  saveButton.addEventListener("click", () => {
    const newContent = inputField.value;

    fetch(editUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": csrfToken,
      },
      body: new URLSearchParams({ content: newContent }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "Message updated") {
          chatSocket.send(
            JSON.stringify({
              edit_message: {
                message_id: messageId,
                new_content: newContent,
              },
            })
          );

          inputField.replaceWith(contentElement);
          contentElement.innerHTML =
            wrapEditedContentWithAnchorTags(newContent);

          let editedIndicator = messageElement.querySelector(".message-edited");
          if (!editedIndicator) {
            editedIndicator = document.createElement("div");
            editedIndicator.classList.add("message-edited");
            editedIndicator.innerText = translate("Edited");
            contentElement.insertAdjacentElement("afterend", editedIndicator);
          }

          isTextareaOpened = false;
          saveButton.remove();
          cancelButton.remove();
          editButton.style.display = "";
          pinButton.style.display = "";
        } else {
          alert(data.error);
          if (data.error === "Message editing time limit exceeded") {
            cancelEdit();
            editButton.style.display = "none";
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        cancelEdit();
      });
  });

  cancelButton.addEventListener("click", cancelEdit);

  const sendButton = document.querySelector(".send-button");
  if (sendButton && inputField) {
    sendButton.addEventListener("click", () => {
      if (isTextareaOpened) {
        cancelEdit();
      }
    });
  }
}

function getFormattedDateHeader(dateString) {
  const date = new Date(dateString);
  const options = { day: "numeric", month: "long", year: "numeric" };
  return date.toLocaleDateString(undefined, options);
}

function togglePinMessage(messageId, button) {
  const messagesContainer = document.getElementById("chat-messages");
  const pinMessageTemplate = messagesContainer.getAttribute(
    "data-pin-message-url"
  );
  const togglePinUrl = pinMessageTemplate.replace("/0/", `/${messageId}/`);

  fetch(togglePinUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      if (!button.classList.contains("unpin-message")) {
        button.textContent =
          data.action === "pinned" ? translate("Unpin") : translate("Pin");
      }
      loadPinnedMessages();
    })
    .catch((error) => console.error("Error:", error));
}

let socket;

document.addEventListener("DOMContentLoaded", function () {
  const chatLoading = document.getElementById("chat-loading");
  const chatContainer = document.getElementById("chat-container");
  const chatMessagesContainer = document.getElementById("chat-messages");
  const currentUserId = parseInt(chatContainer.getAttribute("data-user-id"));
  const recipientId = parseInt(chatContainer.getAttribute("data-recipient-id"));
  const getMessagesUrl = chatContainer.getAttribute("data-get-messages");
  const loadMoreButton = document.getElementById("load-more-private-messages");
  const noMessagesText = translate("No messages. Say something!");

  let currentOffset = 20;
  let allMessagesLoaded = false;

  function generateMessageHTML(message) {
    const isCurrentUser = message.sender_id === currentUserId;
    const formattedTimestamp = formatTimestamp(message.created_at);
    const isPinned = message.is_pinned;

    return `
      <div class="message-wrapper ${
        isCurrentUser ? "sent" : "received"
      }" data-message-id="${message.id}">
        <img src="${
          message.profile_picture_url
        }" alt="Profile Picture" class="chat-profile-picture">
        <div class="message-box ${isCurrentUser ? "sent" : "received"}">
          <div class="message-content-wrapper" data-creation-time="${
            message.created_at
          }">
            <div class="message-content">${wrapUrlsWithAnchorTags(
              message.message
            )}</div>
            ${
              message.file
                ? `<div class="message-file">
                    ${translate("File Attachment: ")}<a href="${
                  message.file
                }" download="${getFileNameFromUrl(
                  message.file
                )}" class="file-link">
                        ${getFileNameFromUrl(message.file)}
                    </a>
                    ${
                      message.file_size
                        ? ` (${formatFileSize(message.file_size)})`
                        : ""
                    }
                </div>`
                : ""
            }
            ${
              message.edited
                ? `<div class="message-edited">${translate("Edited")}</div>`
                : ""
            }
            <div class="message-timestamp">${formattedTimestamp}</div>
            ${
              isCurrentUser
                ? `<button class="edit-message-button">${translate(
                    "Edit"
                  )}</button>`
                : ""
            }
            <button class="pin-message-button" data-message-id="${
              message.id
            }" data-is-pinned="${isPinned}">
              ${isPinned ? translate("Unpin") : translate("Pin")}
            </button>
          </div>
        </div>
      </div>`;
  }

  function startWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const chatSocketUrl = `${protocol}://${window.location.host}/ws/private_chat/${recipientId}/`;
    socket = new WebSocket(chatSocketUrl);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const messageHTML = generateMessageHTML(data);

      chatMessagesContainer.innerHTML += messageHTML;
      scrollToBottom();
      checkForMessages();

      const editButtons = document.querySelectorAll(".edit-message-button");
      editButtons.forEach((editButton) => {
        editButton.removeEventListener("click", handleEditButtonClick);
        editButton.addEventListener("click", handleEditButtonClick);
      });

      handleScroll();
    };

    socket.onclose = (e) => {
      console.error("WebSocket connection closed unexpectedly.");
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  function checkForMessages() {
    if (chatMessagesContainer.innerHTML.trim() === "") {
      chatMessagesContainer.innerHTML = `<p class="no-messages-text">${noMessagesText}</p>`;
    } else {
      const noMessagesElement = document.querySelector(".no-messages-text");
      if (noMessagesElement) {
        noMessagesElement.remove();
      }
    }
  }

  function scrollToBottom() {
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  }

  function loadPrivateMessages(offset, limit) {
    if (allMessagesLoaded) return;

    fetch(`${getMessagesUrl}?offset=${offset}&limit=${limit}`)
      .then((response) => response.json())
      .then((messages) => {
        if (messages.length === 0) {
          allMessagesLoaded = true;
          loadMoreButton.style.display = "none";
          return;
        }

        const fragment = document.createDocumentFragment();

        messages.forEach((message) => {
          const messageHTML = generateMessageHTML(message);

          const tempElement = document.createElement("div");
          tempElement.innerHTML = messageHTML.trim();
          fragment.prepend(tempElement.firstChild);
        });

        chatMessagesContainer.prepend(fragment);
        moveDateHeaderToTop()
      })
      .catch((error) => console.error("Error loading messages:", error));
  }

  chatMessagesContainer.addEventListener("scroll", function () {
    if (chatMessagesContainer.scrollTop === 0 && !allMessagesLoaded) {
      loadMoreButton.style.display = "block";
    } else {
      loadMoreButton.style.display = "none";
    }
  });

  loadMoreButton.addEventListener("click", function () {
    loadPrivateMessages(currentOffset, 30);
    currentOffset += 30;
  });

  startWebSocket();

  function getFileNameFromUrl(url) {
    const decodedUrl = decodeURIComponent(url);
    return decodedUrl.substring(decodedUrl.lastIndexOf("/") + 1);
  }

  function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    let hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12;
    hours = hours ? hours : 12;
    const minutesStr = minutes < 10 ? "0" + minutes : minutes;
    return `${hours}:${minutesStr} ${ampm}`;
  }

  function handleEditButtonClick(event) {
    const messageId = event.target
      .closest(".message-wrapper")
      .getAttribute("data-message-id");
    editMessage(messageId);
  }

  setInterval(() => {
    const messageWrappers = document.querySelectorAll(".message-wrapper");
    messageWrappers.forEach((wrapper) => {
      const messageId = wrapper.getAttribute("data-message-id");
      const editButton = wrapper.querySelector(".edit-message-button");
      const inputField = wrapper.querySelector("textarea.edit-textarea");
      const saveButton = wrapper.querySelector(".save-message-button");

      if (editButton) {
        const creationTime = wrapper
          .querySelector(".message-content-wrapper")
          .getAttribute("data-creation-time");
        if (!isNewMessage(creationTime)) {
          editButton.style.display = "none";
          if (inputField && saveButton) {
            saveButton.click();
          }
        }
      }
    });
  }, 5000);

  document.addEventListener("click", function (event) {
    if (event.target.classList.contains("pin-message-button")) {
      const messageId = event.target.getAttribute("data-message-id");
      togglePinMessage(messageId, event.target);
    }
  });

  function wrapUrlsWithAnchorTags(content) {
    const urlRegex = /(https?:\/\/[^\s]+)/g;

    return content.replace(urlRegex, (url) => {
      return `<a href="${url}" onclick="return confirmVisit('${url}')" target="_blank">${url}</a>`;
    });
  }

  function checkForMessages() {
    const loadingDiv = document.querySelector(".loading-messages");
    const noMessagesDiv = document.querySelector(".no-messages");
    if (loadingDiv) {
      loadingDiv.remove();
    }

    if (chatLoading.children.length === 0) {
      if (noMessagesDiv) {
        noMessagesDiv.remove();
      }
      chatLoading.innerHTML = `<div class="no-messages">${noMessagesText}</div>`;
    } else {
      if (noMessagesDiv) {
        noMessagesDiv.remove();
      }
    }
  }

  function showLoading() {
    const loadingText = translate("Loading Messages...");
    chatLoading.innerHTML = `<div class="loading-messages">${loadingText}</div>`;
  }

  showLoading();
  scrollToBottom();
  setTimeout(checkForMessages, 1000);
  initializeDateHeader();
  chatMessagesContainer.addEventListener("scroll", handleScroll);
});

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("myForm");
  const sendButton = document.getElementById("send-button");
  const textarea = document.getElementById("chat-message-input");

  textarea.addEventListener("input", () => {
    sendButton.disabled = !textarea.value.trim();
  });

  form.addEventListener("submit", submit);
});

function moveDateHeaderToTop() {
  const chatMessagesContainer = document.getElementById("chat-messages");
  const dateHeader = document.getElementById("date-header");

  if (dateHeader) {
    chatMessagesContainer.insertBefore(dateHeader, chatMessagesContainer.firstChild);
  }
}


function handleScroll() {
  const chatMessagesContainer = document.getElementById("chat-messages");
  const messages = chatMessagesContainer.querySelectorAll(".message-wrapper");
  const dateHeader = document.getElementById("date-header");
  const containerTop = chatMessagesContainer.scrollTop;
  let newDateHeader = "";

  if (messages.length > 0) {
    for (let i = 0; i < messages.length; i++) {
      const messageTop = messages[i].offsetTop;
      if (messageTop >= containerTop) {
        const messageDate = new Date(
          messages[i].querySelector(
            ".message-content-wrapper"
          ).dataset.creationTime
        );
        newDateHeader = getFormattedDateHeader(messageDate.toISOString());
        break;
      }
    }

    if (newDateHeader !== dateHeader.textContent) {
      dateHeader.textContent = newDateHeader;
    }
    dateHeader.style.display = "block";
  } else {
    dateHeader.style.display = "none";
  }
}

function initializeDateHeader() {
  const chatMessagesContainer = document.getElementById("chat-messages");
  const messages = chatMessagesContainer.querySelectorAll(".message-wrapper");
  const dateHeader = document.getElementById("date-header");
  if (messages.length > 0) {
    const firstMessageDate = new Date(
      messages[0].querySelector(".message-content-wrapper").dataset.creationTime
    );
    dateHeader.textContent = getFormattedDateHeader(
      firstMessageDate.toISOString()
    );
    dateHeader.style.display = "block";
  } else {
    dateHeader.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("myForm");
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

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("clear-chat-button")
    .addEventListener("click", function (event) {
      if (confirm(translate("Are you sure you want to delete all messages?"))) {
        const url = this.getAttribute("data-url");
        fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              document.querySelector(".chat-messages").innerHTML = "";
              location.reload();
            }
          })
          .catch((error) => {
            console.error("Error:", error);
          });
      } else {
        return false;
      }
    });
});

document.addEventListener("click", function (event) {
  const menu = document.getElementById("options-menu");
  if (
    !menu.contains(event.target) &&
    !event.target.classList.contains("options-button")
  ) {
    menu.style.display = "none";
  }
});


document.getElementById("pinned-messages-button").addEventListener("click", function () {
    const dropdown = document.getElementById("pinned-messages-dropdown");
    dropdown.style.display =
      dropdown.style.display === "none" || dropdown.style.display === ""
        ? "block"
        : "none";

    if (dropdown.style.display === "block") {
      loadPinnedMessages();
    }
  });

document.addEventListener("click", function (event) {
  const isClickInside =
    document.getElementById("pinned-messages-button").contains(event.target) ||
    document.getElementById("pinned-messages-dropdown").contains(event.target);

  if (!isClickInside) {
    document.getElementById("pinned-messages-dropdown").style.display = "none";
  }
});
