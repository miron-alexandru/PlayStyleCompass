const getStarRating = (score) => {
  let starsHtml = "";
  for (let i = 1; i <= 5; i++) {
    starsHtml += `<i class="fas fa-star ${
      i <= score ? "gold-star" : "empty-star"
    }"></i>`;
  }
  return starsHtml;
};


function decodeHTMLEntities(text) {
  let textArea = document.createElement("textarea");
  textArea.innerHTML = text;
  return textArea.value;
}

document.querySelectorAll(".review-description-container").forEach(function (container) {
  let truncatedText = container.querySelector(".review-description");
  let fullText = container.querySelector(".review-description-full");
  let readButton = container.querySelector(".read-button-review");

  truncatedText.innerHTML = decodeHTMLEntities(truncatedText.innerHTML);
  fullText.innerHTML = decodeHTMLEntities(fullText.innerHTML);

  if (truncatedText.textContent.trim() === fullText.textContent.trim()) {
    readButton.style.display = "none";
  } else {
    readButton.style.display = "inline";
  }

  readButton.addEventListener("click", function () {
    if (truncatedText.style.display === "none") {
      truncatedText.style.display = "inline";
      fullText.style.display = "none";
      readButton.textContent = translate("[Read more...]");
    } else {
      truncatedText.style.display = "none";
      fullText.style.display = "inline";
      readButton.textContent = translate("[Read less...]");
    }
  });
});


document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".star-rating").forEach((element) => {
    const score = parseInt(element.getAttribute("data-score"), 10);
    element.innerHTML = getStarRating(score);
  });
});


const showUserMessage = (container, message) => {
  let customMessage = document.createElement("div");
  customMessage.className = "error-message";
  customMessage.textContent = message;
  container.appendChild(customMessage);

  setTimeout(() => {
    customMessage.classList.add("fade-out");
    setTimeout(() => {
      customMessage.remove();
    }, 1000);
  }, 3000);
};

document.querySelectorAll(".author-name").forEach((link) => {
  link.addEventListener("click", function (event) {
    event.preventDefault();
    let profileUrl = this.href;
    let container = this.closest(".author-container");

    fetch(profileUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then((response) => response.json())
      .then((data) => {
        if (!data.exists) {
          showUserMessage(container, "User does not exist or has deleted their account!");
        } else {
          window.open(profileUrl, "_blank");
        }
      })
      .catch(() => {
        window.open(profileUrl, "_blank");
      });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const showMessage = (container, message) => {
    let customMessage = $(`<div class="success-message">${message}</div>`);
    container.append(customMessage);

    setTimeout(() => {
      customMessage.fadeOut("slow", function () {
        customMessage.remove();
      });
    }, 3000);
  };

  const sendRatingAction = (actionType, event) => {
    event.preventDefault();

    let thisContainer = $(event.target).closest(".like-dislike");
    let reviewId = thisContainer.closest(".review").data("review-id");
    let ratingUrl = thisContainer.data(`${actionType}-url`);

    $.ajax({
      type: "POST",
      url: ratingUrl,
      headers: {
        "X-CSRFToken": csrfToken,
      },
      data: {
        review_id: reviewId,
      },
      success: function (data) {
        showMessage(thisContainer, data["message"]);

        // Update like and dislike counts
        thisContainer.find(".like-count").text(data.likes);
        thisContainer.find(".dislike-count").text(data.dislikes);
      },
      error: function (error) {
        console.error(`Error incrementing ${actionType}:`, error);
      },
    });
  };

  // Attach event listeners
  $(document).on("click", ".thumbs-up", function (event) {
    sendRatingAction("like", event);
  });

  $(document).on("click", ".thumbs-down", function (event) {
    sendRatingAction("dislike", event);
  });
});
