document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.unblock-button').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            const unblockUrl = this.getAttribute('data-unblock-url');
            const userId = this.getAttribute('data-user-id');
            const blockItem = document.getElementById(`block-item-${userId}`);

            fetch(unblockUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.message == 'User has been unblocked.') {
                    alert(data.message);
                    blockItem.remove();
                } else {
                    alert(data.message || data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while trying to unblock the user.');
            });
        });
    });
});
