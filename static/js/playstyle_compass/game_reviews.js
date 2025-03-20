const getStarRating = (score) => {
  let starsHtml = "";
  for (let i = 1; i <= 5; i++) {
    starsHtml += `<i class="fas fa-star ${
      i <= score ? "gold-star" : "empty-star"
    }"></i>`;
  }
  return starsHtml;
};

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".star-rating").forEach((element) => {
    const score = parseInt(element.getAttribute("data-score"), 10);
    element.innerHTML = getStarRating(score);
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
