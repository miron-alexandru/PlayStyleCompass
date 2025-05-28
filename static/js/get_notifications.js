fetch(authCheckUrl)
  .then((response) => response.json())
  .then((data) => {
    if (data.authenticated) {
      const notifications = [];
      const notificationsElement = document.getElementById("notifications");
      const markReadUrl = notificationsElement.dataset.markRead;
      const markInactiveUrl = notificationsElement.dataset.markInactive;
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      document.cookie = "django_timezone=" + timezone;

      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const notifySocket = new WebSocket(
        `${protocol}://${window.location.host}/ws/notify/`
      );

      notifySocket.onmessage = function (e) {
        if (notifySocket.readyState === WebSocket.OPEN) {
          const data = JSON.parse(e.data);

          if (data.delivered) {
            addNotification(data);
          }
        }
      };

      const addNotification = function (data) {
        notifications.push(data);
        updateNotifications();
      };

      const handleNotificationAction = (index, actionType) => {
        const notificationId = notifications[index].id;
        const notificationsElement = document.getElementById("notifications");
        let url;

        switch (actionType) {
          case "markRead":
            url = markReadUrl;
            break;
          case "markInactive":
            url = markInactiveUrl;
            break;
          default:
            return;
        }

        url = url.replace("/0", `/${notificationId}`);

        fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              if (actionType === "markRead") {
                notifications[index].is_read = true;
              } else if (actionType === "markInactive") {
                notifications[index].is_active = false;
              }

              updateNotifications();
            } else {
              console.error(`Failed to mark notification as ${actionType}`);
            }
          })
          .catch((error) => console.error("Error:", error));
      };

      const markAllNotifications = (actionType) => {
        const notificationsElement = document.getElementById("notifications");
        let url;

        switch (actionType) {
          case "markRead":
            url = markReadUrl;
            break;
          case "markInactive":
            url = markInactiveUrl;
            break;
          default:
            console.error("Invalid actionType");
            return;
        }

        url = url.replace("/0", "");

        fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              notifications.forEach((notification) => {
                if (
                  actionType === "markRead" ||
                  actionType === "markInactive"
                ) {
                  if (actionType === "markRead" && !notification.is_read) {
                    notification.is_read = true;
                  } else if (actionType === "markInactive") {
                    notification.is_active = false;
                  }
                }
              });

              if (actionType === "markInactive") {
                removeAllNotifications();
              }

              updateNotifications();
            } else {
              console.error(
                `Failed to mark all notifications as ${actionType}.`
              );
            }
          })
          .catch((error) => console.error("Error:", error));
      };

      const markNotificationAsRead = (index) => {
        handleNotificationAction(index, "markRead");
      };

      const removeNotification = (index) => {
        handleNotificationAction(index, "markInactive");
        notifications.splice(index, 1);

        const ulElement = document.getElementById("notify");
        const notificationElementToRemove = ulElement.children[index];

        if (notificationElementToRemove) {
          notificationElementToRemove.remove();
        }

        updateNotifications();
      };

      const removeAllNotifications = () => {
        const ulElement = document.getElementById("notify");

        ulElement.innerHTML = "";
        notifications.length = 0;

        updateNotifications();
      };

      const formatDate = (timestamp) => {
        const date = new Date(timestamp);

        const options = {
          timeZone: timezone,
          month: "long",
          day: "numeric",
          year: "numeric",
          hour: "numeric",
          minute: "numeric",
          hour12: true,
        };

        return date.toLocaleString("en-US", options);
      };

      const updateNotifications = () => {
        const ulElement = document.getElementById("notify");
        ulElement.innerHTML = "";

        if (notifications.length === 0) {
          const emptyMessage = document.createElement("li");
          emptyMessage.textContent = translate("Nothing to report");
          emptyMessage.className = "empty-notifications";
          ulElement.appendChild(emptyMessage);
          document.getElementById("bellCount").setAttribute("data-count", 0);
          return;
        }

        let unreadCount = 0;

        notifications.sort(
          (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
        );

        const buttonContainer = document.createElement("div");
        buttonContainer.className = "button-container";

        const markAllReadBtn = document.createElement("button");
        markAllReadBtn.className = "mark-all-read-btn";
        const markAllIconHtml = '<span class="mark-icon">&#10003;</span>';
        const translatedMarkAll = translate("Mark as read")
        markAllReadBtn.innerHTML = `${markAllIconHtml} ${translatedMarkAll}`
        markAllReadBtn.title = translate("Mark All Notifications as Read");
        markAllReadBtn.addEventListener("click", () =>
          markAllNotifications("markRead")
        );

        const markAllInactiveBtn = document.createElement("button");
        markAllInactiveBtn.className = "mark-all-inactive-btn";
        const deleteIconHTML = '<span class="delete-icon"><i class="fa-solid fa-xmark"></i></span>';
        const translatedDelete = translate("Delete All");
        markAllInactiveBtn.innerHTML = `${deleteIconHTML} ${translatedDelete}`;
        markAllInactiveBtn.title = translate("Delete All Notifications");
        markAllInactiveBtn.addEventListener("click", () =>
          markAllNotifications("markInactive")
        );

        buttonContainer.appendChild(markAllReadBtn);
        buttonContainer.appendChild(markAllInactiveBtn);

        ulElement.appendChild(buttonContainer);

        notifications.forEach(function (notification, index) {
          const newLi = document.createElement("li");
          const notificationContainer = document.createElement("div");
          notificationContainer.className = "notification-container";

          const newAnchor = document.createElement("a");
          newAnchor.className = "dropdown-item text-wrap";
          newAnchor.classList.add(
            notification.is_read ? "notification-read" : "notification-unread"
          );
          newAnchor.title = translate("Click to mark as read");

          if (!notification.is_read) {
            newAnchor.addEventListener("click", function () {
              markNotificationAsRead(index);
            });
          }

          const notificationContent = document.createElement("div");
          notificationContent.className = "notification-content";

          const message = document.createElement("div");
          message.className = "notification-message";
          message.innerHTML = notification.message;

          const timestamp = document.createElement("div");
          timestamp.className = "notification-timestamp";
          timestamp.textContent = formatDate(notification.timestamp);

          const closeButton = document.createElement("button");
          closeButton.className = "btn-close";
          closeButton.innerHTML =
            '<span class="single-delete-icon"><i class="fa-solid fa-circle-xmark"></i></span>';
          closeButton.title = translate("Delete this notification");

          closeButton.addEventListener("click", function () {
            removeNotification(index);
          });

          notificationContent.appendChild(message);
          notificationContent.appendChild(timestamp);
          notificationContainer.appendChild(notificationContent);
          notificationContainer.appendChild(closeButton);
          newAnchor.appendChild(notificationContainer);
          newLi.appendChild(newAnchor);

          ulElement.appendChild(newLi);

          const separator = document.createElement("div");
          separator.className = "notification-separator";
          ulElement.appendChild(separator);

          if (!notification.is_read) {
            unreadCount++;
          }
        });

        ulElement.lastElementChild.remove();

        document
          .getElementById("bellCount")
          .setAttribute("data-count", unreadCount);
      };

      updateNotifications();
    }
  })
  .catch((error) => console.error("Error:", error));
