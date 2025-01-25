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

  let messages = document.querySelectorAll(
    '.message .alert:not([style="display: none;"])'
  );
  messages.forEach(function (message) {
    setTimeout(function () {
      let closeButton = message.querySelector(".close");
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
    let $dropdownContainer = $(this).find(".dropdown-menu");

    $dropdownToggle.on("click", function (e) {
      e.preventDefault();

      $dropdownContainer.toggle();
    });
  });

  $(document).on("click", function (event) {
    if (!$(event.target).closest(".nav-item.dropdown").length) {
      $(".dropdown-menu").hide();
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
  $(".profile-name")
    .mouseenter(function () {
      let $this = $(this);
      let $tooltip = $this.siblings(".custom-tooltip");

      if ($this[0].scrollWidth > $this[0].clientWidth) {
        $tooltip.show();
      }
    })
    .mouseleave(function () {
      let $tooltip = $(this).siblings(".custom-tooltip");
      $tooltip.hide();
    });
});

let lastScrollTop = 0;

$(window).on("scroll", function () {
  const windowWidth = $(window).width();
  if (windowWidth <= 1100) return;

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

document.addEventListener("DOMContentLoaded", function () {
  const resendLink = document.getElementById("resend-link");
  if (resendLink) {
    resendLink.addEventListener("click", function (event) {
      event.preventDefault();
      const emailUrl = document
        .getElementById("resend-email")
        .getAttribute("data-email-url");

      fetch(emailUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({}),
      }).catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  fetch(authCheckUrl)
    .then((response) => response.json())
    .then((data) => {
      if (data.authenticated) {
        const recipientMeta = document.getElementById("recipient-id");
        let recipientId = "";

        if (recipientMeta) {
          recipientId = Number(recipientMeta.getAttribute("content"));
        }

        const wsUrl = recipientId
          ? `wss://${window.location.host}/ws/online-status/${recipientId}/`
          : `wss://${window.location.host}/ws/online-status/`;

        const ws = new WebSocket(wsUrl);

        ws.onmessage = function (event) {
          const data = JSON.parse(event.data);
          const statusElement = document.getElementById("status");
          const lastSeenElement = document.querySelector(".last-seen");

          if (statusElement) {
            statusElement.innerText = data.status
              ? translate("Online")
              : translate("Offline");

            if (data.status) {
              statusElement.classList.remove("offline");
              statusElement.classList.add("online");
            } else {
              statusElement.classList.remove("online");
              statusElement.classList.add("offline");
            }
          }

          if (lastSeenElement) {
            if (data.status) {
              lastSeenElement.style.display = "none";
            } else {
              lastSeenElement.style.display = "block";
              lastSeenElement.innerHTML = `<strong>(Last Seen: </strong>${data.last_online})`;
            }
          }
        };

        ws.onerror = function (error) {
          console.error("WebSocket error:", error);
        };
      }
    })
    .catch((error) => {
      console.error("Auth check failed:", error);
    });
});


function updateLanguage(event, language) {
  event.preventDefault();
  const changeLanguageUrl = document.querySelector('.language-options').getAttribute('data-change-language-url');

  fetch(changeLanguageUrl, {
      method: "POST",
      headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
      },
      body: JSON.stringify({ language: language }),
  }).then((response) => {
      if (response.ok) {
          const currentPath = window.location.pathname;
          const newPath = `/${language}${currentPath.slice(3)}`;

          window.location.href = newPath;
      } else {
          console.error("Failed to update language in user profile");
      }
  });
}
