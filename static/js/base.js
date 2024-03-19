document.addEventListener("DOMContentLoaded", function () {
  let descriptionContent = document
    .getElementById("description-content")
    .innerHTML.trim();
  let pageDescription = document.querySelector(".header-desc");

  let headerContent = document
    .getElementById("header-content")
    .innerHTML.trim();
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
  let descriptionContent = document
    .getElementById("description-content")
    .innerHTML.trim();
  let pageDescription = document.querySelector(".header-desc");

  if (descriptionContent.length > 0) {
    pageDescription.classList.add("border-bottom");
  } else {
    pageDescription.style.display = "none";
  }
});


document.addEventListener("DOMContentLoaded", function () {
  let closeButtons = document.querySelectorAll(".message .close");

  closeButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      let alertDiv = button.closest(".alert");
      alertDiv.classList.add("fade-out");

      setTimeout(function () {
        alertDiv.style.display = "none";

        let visibleAlerts = document.querySelectorAll(
          '.message .alert:not([style="display: none;"])'
        );

        if (visibleAlerts.length === 0) {
          document.querySelector(".message").style.display = "none";
        }
      }, 500);
    });
  });

  let messages = document.querySelectorAll('.message .alert:not([style="display: none;"])');
  messages.forEach(function (message) {
    setTimeout(function () {
      let closeButton = message.querySelector('.close');
      closeButton.click();
    }, 5000);
  });
});


const profilePictureUpload = document.getElementById("profile-picture-upload");

if (profilePictureUpload) {
  profilePictureUpload.addEventListener("change", function () {
    const fileInput = this;
    const file = fileInput.files[0];

    if (file) {
      const reader = new FileReader();

      reader.onload = function (e) {
        const profilePicture = document.getElementById("profile-picture");
        const userProfilePicture = document.getElementById(
          "profile-picture-user-profile"
        );

        if (profilePicture) {
          profilePicture.src = e.target.result;
        }

        if (userProfilePicture) {
          userProfilePicture.src = e.target.result;
        }

        const formData = new FormData();
        formData.append("profile_picture", file);

        const profileUrl = fileInput.getAttribute("data-profile-url");
        const csrfToken = fileInput.getAttribute("data-csrf-token");

        fetch(profileUrl, {
          method: "POST",
          body: formData,
          headers: {
            "X-CSRFToken": csrfToken,
          },
        });
      };

      reader.readAsDataURL(file);
    }
  });
}

$(document).ready(function () {
  $(".nav-item.dropdown").each(function () {
    let $dropdownToggle = $(this).find(".dropdown-toggle");
    let $dropdownContainer = $(this).find(".dropdown-container");

    $dropdownToggle.on("click", function (e) {
      e.preventDefault();

      $dropdownContainer.toggle();
    });
  });


$(document).on("click", function (event) {
    if (!$(event.target).closest(".nav-item.dropdown").length) {
      $(".dropdown-container").hide();
    }
  });
});


$(document).ready(function () {
  $(window).scroll(function () {
    if ($(this).scrollTop() > 75) {
      $(".scroll-top-container").addClass("scroll-top-visible");
    } else {
      $(".scroll-top-container").removeClass("scroll-top-visible");
    }
  });

  $("#scroll-top").click(function () {
    $("html, body").animate({ scrollTop: 0 }, "slow");
    return false;
  });
});


$(document).ready(function () {
    $('.profile-name').mouseenter(function () {
        let $this = $(this);
        let $tooltip = $this.siblings('.custom-tooltip');

        if ($this[0].scrollWidth > $this[0].clientWidth) {
            $tooltip.show();
        }
    }).mouseleave(function () {
        let $tooltip = $(this).siblings('.custom-tooltip');
        $tooltip.hide();
    });
});


let lastScrollTop = 0;

$(window).on("scroll", function() {
    const scrollTop = $(this).scrollTop();

    if (scrollTop === 0) {
        $(".navbar").removeClass("fixed");
    } else if (scrollTop > lastScrollTop) {
        $(".navbar").removeClass("fixed");
    } else {
        $(".navbar").addClass("fixed");
    }
    lastScrollTop = scrollTop;
});