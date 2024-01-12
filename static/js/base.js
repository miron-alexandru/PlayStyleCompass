document.addEventListener("DOMContentLoaded", function () {
  let descriptionContent = document.getElementById("description-content").innerHTML.trim();
  let pageDescription = document.querySelector(".header-desc");

  let headerContent = document.getElementById("header-content").innerHTML.trim();
  let pageHeader = document.querySelector(".page-header");

  if (descriptionContent.length > 0) {
    pageDescription.classList.add("border-bottom");
  } else {
    pageDescription.style.display = "none";
    pageHeader.style.marginBottom = "7px";
  }

  if (headerContent.length === 0) {
    pageHeader.style.display = "none";
  }

});


document.addEventListener("DOMContentLoaded", function () {
  let descriptionContent = document.getElementById("description-content").innerHTML.trim();
  let pageDescription = document.querySelector(".header-desc");

  if (descriptionContent.length > 0) {
    pageDescription.classList.add("border-bottom");
  } else {
    pageDescription.style.display = "none";
  }
});

document.addEventListener('DOMContentLoaded', function () {
  let closeButtons = document.querySelectorAll('.message .close');

  closeButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      let alertDiv = button.closest('.alert');
      alertDiv.classList.add('fade-out');

      setTimeout(function () {
        alertDiv.style.display = 'none';

        let visibleAlerts = document.querySelectorAll('.message .alert:not([style="display: none;"])');

        if (visibleAlerts.length === 0) {
          document.querySelector('.message').style.display = 'none';
        }
      }, 500);
    });
  });
});


const profilePictureUpload = document.getElementById('profile-picture-upload');

if (profilePictureUpload) {
  profilePictureUpload.addEventListener('change', function () {
    const fileInput = this;
    const file = fileInput.files[0];

    if (file) {
      const reader = new FileReader();

      reader.onload = function (e) {
        const profilePicture = document.getElementById('profile-picture');
        const userProfilePicture = document.getElementById('profile-picture-user-profile');

        if (profilePicture) {
          profilePicture.src = e.target.result;
        }

        if (userProfilePicture) {
          userProfilePicture.src = e.target.result;
        }

        const formData = new FormData();
        formData.append('profile_picture', file);

        const profileUrl = fileInput.getAttribute('data-profile-url');
        const csrfToken = fileInput.getAttribute('data-csrf-token');

        fetch(profileUrl, {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': csrfToken,
          },
        });
      };

      reader.readAsDataURL(file);
    }
  });
}


function checkScroll() {
  const windowWidth = $(window).width();

  if (windowWidth > 1000) {
    const startY = $('.navbar').height() * 2 + 500;

    if ($(window).scrollTop() > startY) {
      $('.navbar').addClass("fixed");
    } else {
      $('.navbar').removeClass("fixed");
    }
  } else {
    $('.navbar').removeClass("fixed");
  }
}

if ($('.navbar').length > 0) {
  $(window).on("scroll load resize", function () {
    checkScroll();
  });
}



$(document).ready(function () {
  $('.nav-item.dropdown').each(function () {
    let $dropdownToggle = $(this).find('.dropdown-toggle');
    let $dropdownContainer = $(this).find('.dropdown-container');

    $dropdownToggle.on('click', function (e) {
      e.preventDefault(); // Prevent the default link behavior

      $dropdownContainer.toggle();
    });
  });

  // Hide dropdowns when clicking outside of them
  $(document).on('click', function (event) {
    if (!$(event.target).closest('.nav-item.dropdown').length) {
      $('.dropdown-container').hide();
    }
  });
});


$(document).ready(function () {
  $(window).scroll(function () {
    if ($(this).scrollTop() > 75) {
      $('.scroll-top-container').addClass('scroll-top-visible');
    } else {
      $('.scroll-top-container').removeClass('scroll-top-visible');
    }
  });

  $('#scroll-top').click(function () {
    $('html, body').animate({ scrollTop: 0 }, 'slow');
    return false;
  });
});



const notifyScoket = new WebSocket(
    'ws://' +
    window.location.host +
    '/ws/notify/'
);

notifyScoket.onopen = function (e) {
    console.log('Socket successfully connected.');
};

notifyScoket.onclose = function (e) {
    console.log('Socket closed unexpectedly');
};

notifyScoket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const message = data.message;

    setMessage(message);
};

function setMessage(message) {
    var newLi = document.createElement('li');

    var newAnchor = document.createElement('a');
    newAnchor.className = 'dropdown-item text-wrap';
    newAnchor.href = '#';
    newAnchor.textContent = message;

    newLi.appendChild(newAnchor);

    var ulElement = document.getElementById('notify');

    ulElement.appendChild(newLi);

    count = document.getElementById('bellCount').getAttribute('data-count');
    document.getElementById('bellCount').setAttribute('data-count', parseInt(count) + 1);
}

