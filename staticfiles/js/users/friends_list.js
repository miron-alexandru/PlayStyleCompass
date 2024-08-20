function onRemoveFriend() {
  location.reload();
}

function triggerRemoveFriend(friend_id) {
  removeFriend(friend_id, onRemoveFriend);
}

document.addEventListener("DOMContentLoaded", function() {
    const friends = document.querySelectorAll('.friend-card');
    const statusMap = new Map();

    friends.forEach(friend => {
        const recipientId = Number(friend.querySelector('.recipient-id').getAttribute('content'));
        const wsUrl = recipientId ? 
            `ws://${window.location.host}/ws/online-status/${recipientId}/` : 
            `ws://${window.location.host}/ws/online-status/`;

        const ws = new WebSocket(wsUrl);

        statusMap.set(recipientId, {
            ws: ws,
            statusElement: friend.querySelector('.status')
        });

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const { statusElement } = statusMap.get(recipientId);

            if (statusElement) {
                statusElement.innerText = data.status ? translate('Online') : translate('Offline');

                if (data.status) {
                    statusElement.classList.remove('offline');
                    statusElement.classList.add('online');
                } else {
                    statusElement.classList.remove('online');
                    statusElement.classList.add('offline');
                }
            }
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    });
});

