$(document).ready(function() {
  function getCSRFToken() {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, 10) === 'csrftoken=') {
          cookieValue = decodeURIComponent(cookie.substring(10));
          break;
        }
      }
    }
    return cookieValue;
  }

  $('.favorite-toggle').on('click', function() {
    var gameID = $(this).data('game-id');
    var icon = $(this).find('i');
    var isFavorite = $(this).data('is-favorite');
    var csrfToken = getCSRFToken();

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