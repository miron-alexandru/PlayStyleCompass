const getCookie = (name) => {
  const cookieString = document.cookie;
  const cookies = cookieString.split('; ');

  for (const cookie of cookies) {
    const [cookieName, cookieValue] = cookie.split('=');
    if (cookieName === name) {
      return decodeURIComponent(cookieValue);
    }
  }

  return null;
};

$(document).ready(() => {
  const getCSRFToken = () => {
    return getCookie('csrftoken');
  };

  $('.favorite-toggle').on('click', function() {
    let gameID = $(this).data('game-id');
    let icon = $(this).find('i');
    let isFavorite = $(this).data('is-favorite');
    let csrfToken = getCSRFToken();

    $.ajax({
      type: 'POST',
      url: '/toggle_favorite/',
      data: { game_id: gameID },
      headers: {
        'X-CSRFToken': csrfToken,
      },
      success: function(data) {
        if (data.is_favorite) {
          icon.removeClass('far').addClass('fas');
        } else {
          icon.removeClass('fas').addClass('far');
        }
      },
      error: function(xhr, status, error) {
        console.error(error);
      }
    });
  });
});
