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

document.addEventListener('DOMContentLoaded', function() {
  let closeButtons = document.querySelectorAll('.message .close');

  closeButtons.forEach(function(button) {
    button.addEventListener('click', function() {
      let alertDiv = button.closest('.alert');
      alertDiv.classList.add('fade-out');

      setTimeout(function() {
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
        if (profilePicture) {
          profilePicture.src = e.target.result;
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
      window.location.reload();
    }
  });
}
