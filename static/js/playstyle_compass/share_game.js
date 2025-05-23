$(document).ready(function () {
  const showMessage = (container, message, isError = false) => {
    let customMessage = $(
      `<div class="${
        isError ? "shared-failed" : "shared-success"
      }">${message}</div>`
    );
    container.before(customMessage);

    setTimeout(() => {
      customMessage.fadeOut("slow", function () {
        customMessage.remove();
      });
    }, 3000);
  };

  $(".game-container").each(function () {
    const container = $(this);
    const shareButton = container.find(".share-button");
    const friendLinks = container.find(".friend-link");
    const friendDropdown = shareButton.next();
    const shareLink = container.data("share-game");

    shareButton.on("click", function (event) {
      event.preventDefault();
      friendDropdown.toggleClass("show");
    });

    friendLinks.on("click", function (event) {
      event.preventDefault();
      const friendLink = $(this);
      const friendId = friendLink.data("friendId");

      const formData = new URLSearchParams();
      formData.append("receiver_id", friendId);

      fetch(shareLink, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken,
        },
        body: formData.toString(),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            showMessage(container, data.message);
          } else if (data.status === "error") {
            showMessage(container, data.message, true);
          }
        })
        .catch((error) => {
          console.error("Fetch operation error:", error);
          showMessage(container, "An error occurred", true);
        });
    });
  });

  $(document).on("click", function (event) {
    if (!$(event.target).is(".share-button")) {
      $(".friend-dropdown-content").removeClass("show");
    }
  });
});

document.addEventListener('DOMContentLoaded', function () {
  const shareContainers = document.querySelectorAll('.share-link-container');
  shareContainers.forEach(container => {
    const toggleIcon = container.querySelector('.btn-toggle-icon');
    const copyMessage = container.querySelector('.copy-message');
    const gameUrl = container.dataset.gameUrl;

    toggleIcon.addEventListener('click', () => {
      navigator.clipboard.writeText(gameUrl).then(() => {
        copyMessage.style.display = 'inline';
        setTimeout(() => { copyMessage.style.display = 'none'; }, 1500);
      }).catch(() => {
        alert('Copy failed, please copy manually.');
      });
    });
  });
});

