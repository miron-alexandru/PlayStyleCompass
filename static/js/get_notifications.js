const notifications = [];

const notifySocket = new WebSocket(
    'ws://' +
    window.location.host +
    '/ws/notify/'
);

notifySocket.onopen = function (e) {
    console.log('Socket successfully connected.');
};

notifySocket.onclose = function (e) {
    console.log('Socket closed unexpectedly');
};

notifySocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    addNotification(data);
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

                console.log(data);
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
}

function updateNotifications() {
    var ulElement = document.getElementById('notify');
    ulElement.innerHTML = '';

    var unreadCount = 0;

    notifications.forEach(function (notification, index) {
        var newLi = document.createElement('li');
        var newAnchor = document.createElement('a');
        newAnchor.className = 'dropdown-item text-wrap';
        newAnchor.href = '#';
        newAnchor.textContent = notification.message;

        newAnchor.addEventListener('click', function () {
            markNotificationAsRead(index);
        });

        var closeButton = document.createElement('button');
        closeButton.className = 'btn-close';
        closeButton.addEventListener('click', function () {
            removeNotification(index);
        });

        newLi.appendChild(newAnchor);
        newLi.appendChild(closeButton);
        ulElement.appendChild(newLi);

        if (!notification.is_read) {
            unreadCount++;
        }
    });

    document.getElementById('bellCount').setAttribute('data-count', unreadCount);
}
