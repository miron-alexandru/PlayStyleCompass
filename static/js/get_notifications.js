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
    const message = data.message;

    addNotification(message);
};

function addNotification(message) {
    notifications.push({ message });
    updateNotifications();
}

function removeNotification(index) {
    const notificationId = 32;

    fetch(`users/mark_notification_inactive/${notificationId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                notifications[index].is_active = false;

                updateNotifications();
            } else {
                console.error('Failed to mark notification as read');
            }
        })
        .catch(error => console.error('Error:', error));
}

function markNotificationAsRead(index) {
    const notificationId = 32;

    fetch(`users/mark_notification_as_read/${notificationId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                notifications[index].is_read = true;

                updateNotifications();
            } else {
                console.error('Failed to mark notification as read');
            }
        })
        .catch(error => console.error('Error:', error));
}

function updateNotifications() {
    var ulElement = document.getElementById('notify');
    ulElement.innerHTML = '';

    var unreadCount = 0;

    notifications.forEach(function (notification, index) {
        console.log(notification);
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