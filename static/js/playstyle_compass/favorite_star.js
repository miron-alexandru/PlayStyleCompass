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

  const handleToggle = (url, dataKey, iconClasses, successCallback) => {
    return function () {
      let gameID = $(this).data('game-id');
      let icon = $(this).find('i');
      let csrfToken = getCSRFToken();

      $.ajax({
        type: 'POST',
        url: url,
        data: { game_id: gameID },
        headers: {
          'X-CSRFToken': csrfToken,
        },
        success: function (data) {
          if (data[dataKey]) {
            icon.removeClass(iconClasses.inactive).addClass(iconClasses.active);
          } else {
            icon.removeClass(iconClasses.active).addClass(iconClasses.inactive);
          }
          if (successCallback) {
            successCallback(data);
          }
        },
        error: function (xhr, status, error) {
          console.error(error);
        },
      });
    };
  };

  $('.favorite-toggle').on('click', handleToggle('/toggle_favorite/', 'is_favorite', { active: 'fas', inactive: 'far' }));

  $('.queue-toggle').on('click', handleToggle('/toggle_game_queue/', 'in_queue', { active: 'fa-solid', inactive: 'fa-regular' }));
});
