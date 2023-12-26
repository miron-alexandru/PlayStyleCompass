$(document).ready(function () {
  $('.game-container').each(function () {
    const container = $(this);
    const shareButton = container.find('.shareButton');
    const friendLinks = container.find('.friend-link');
    const friendDropdown = shareButton.next();
    const shareLink = container.data('share-game');

    shareButton.on('click', function (event) {
      event.preventDefault();
      friendDropdown.toggleClass('show');
    });

    friendLinks.on('click', function (event) {
      event.preventDefault();
      const friendLink = $(this);
      const friendId = friendLink.data('friendId');

      const formData = new URLSearchParams();
      formData.append('receiver_id', friendId);

      fetch(shareLink, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken,
        },
        body: formData.toString(),
      })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Fetch operation error:', error));
    });
  });

  $(document).on('click', function (event) {
    if (!$(event.target).is('.shareButton')) {
      $('.friend-dropdown-content').removeClass('show');
    }
  });
});
