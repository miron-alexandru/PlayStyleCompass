const notifications = [];
const notifySocket = new WebSocket(`ws://${window.location.host}/ws/notify/`);

notifySocket.onopen = function (e) {
    console.log('Socket successfully connected.');
};

notifySocket.onclose = function (e) {
    console.log('Socket closed unexpectedly');
};

notifySocket.onmessage = function (e) {
    if (notifySocket.readyState === WebSocket.OPEN) {
        const data = JSON.parse(e.data);
        addNotification(data);
    }
};

function addNotification(data) {
    notifications.push(data);
    updateNotifications();
}

function handleNotificationAction(index, actionType) {
    const notificationId = notifications[index].id;
    const notificationsElement = document.getElementById('notifications');
    let url;

    switch (actionType) {
        case 'markRead':
            url = notificationsElement.dataset.markRead;
            break;
        case 'markInactive':
            url = notificationsElement.dataset.markInactive;
            break;
        default:
            return;
    }

    url = url.replace("/0", `/${notificationId}`);

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (actionType === 'markRead') {
                    notifications[index].is_read = true;
                } else if (actionType === 'markInactive') {
                    notifications[index].is_active = false;
                }

                updateNotifications();
            } else {
                console.error(`Failed to mark notification as ${actionType}`);
            }
        })
        .catch(error => console.error('Error:', error));
}

function markNotificationAsRead(index) {
    handleNotificationAction(index, 'markRead');
}

function removeNotification(index) {
    handleNotificationAction(index, 'markInactive');
    notifications.splice(index, 1);

    const ulElement = document.getElementById('notify');
    const notificationElementToRemove = ulElement.children[index];
    
    if (notificationElementToRemove) {
        notificationElementToRemove.remove();
    }

    updateNotifications();
}

function formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function updateNotifications() {
    const ulElement = document.getElementById('notify');
    ulElement.innerHTML = '';

    if (notifications.length === 0) {
        const emptyMessage = document.createElement('li');
        emptyMessage.textContent = 'Nothing to report';
        emptyMessage.className = 'empty-notifications';
        ulElement.appendChild(emptyMessage);
        document.getElementById('bellCount').setAttribute('data-count', 0);
        return;
    }

    let unreadCount = 0;

    notifications.forEach(function (notification, index) {
        const newLi = document.createElement('li');
        const notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';

        const newAnchor = document.createElement('a');
        newAnchor.className = 'dropdown-item text-wrap';
        newAnchor.href = '#';
        newAnchor.title = 'Click to mark as read.';

        newAnchor.addEventListener('click', function () {
            markNotificationAsRead(index);
        });

        const notificationContent = document.createElement('div');
        notificationContent.className = 'notification-content';

        const message = document.createElement('div');
        message.className = 'notification-message';
        message.innerHTML = notification.message;

        const timestamp = document.createElement('div');
        timestamp.className = 'notification-timestamp';
        timestamp.textContent = formatDate(notification.timestamp);

        const closeButton = document.createElement('button');
        closeButton.className = 'btn-close';
        closeButton.title = 'Delete this notification.'

        closeButton.addEventListener('click', function () {
            removeNotification(index);
        });

        notificationContent.appendChild(message);
        notificationContent.appendChild(timestamp);
        notificationContainer.appendChild(notificationContent);
        notificationContainer.appendChild(closeButton);
        newAnchor.appendChild(notificationContainer);
        newLi.appendChild(newAnchor);

        ulElement.appendChild(newLi);

        if (!notification.is_read) {
            unreadCount++;
        }
    });

    document.getElementById('bellCount').setAttribute('data-count', unreadCount);
}

updateNotifications();
