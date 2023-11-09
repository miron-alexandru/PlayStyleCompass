document.addEventListener("DOMContentLoaded", function () {
  var headerContent = document.getElementById("header-content").innerHTML.trim();
  var pageHeader = document.querySelector(".page-header");

  if (headerContent.length > 0) {
    pageHeader.classList.add("border-bottom");
  }
});

document.addEventListener('DOMContentLoaded', function() {
  var closeButtons = document.querySelectorAll('.message .close');

  closeButtons.forEach(function(button) {
    button.addEventListener('click', function() {
      var alertDiv = button.closest('.alert');
      alertDiv.classList.add('fade-out');

      setTimeout(function() {
        alertDiv.style.display = 'none';

        var visibleAlerts = document.querySelectorAll('.message .alert:not([style="display: none;"])');

        if (visibleAlerts.length === 0) {
          document.querySelector('.message').style.display = 'none';
        }
      }, 500);
    });
  });
});


document.getElementById('profile-picture-upload').addEventListener('change', function () {
  const fileInput = this;
  const file = fileInput.files[0];

  if (file) {
    const reader = new FileReader();

    reader.onload = function (e) {
      const profilePicture = document.getElementById('profile-picture');
      profilePicture.src = e.target.result;

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