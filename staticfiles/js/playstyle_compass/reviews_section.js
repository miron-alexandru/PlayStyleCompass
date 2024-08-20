$(document).ready(function () {
  $.getScript("/static/js/playstyle_compass/reviews_template.js", function() {
  });

  $(".game-container").each(function () {
    let container = $(this);

    let initialFetch = true;

    const toggleReviewVisibility = () => {
      let reviewsList = container.find(".reviews-list");

      if (initialFetch) {
        fetchReviews.call(this, reviewsList);
        initialFetch = false;
      } else {
        reviewsList.toggle();
      }
      container
        .find(".show-hide-button")
        .text(
          reviewsList.is(":visible")
            ? translate("Hide Reviews")
            : translate("Show Reviews")
        );
    };

    const fetchReviews = (reviewsList) => {
      let game_id = container.data("game-id");
      let reviewsURL = container.data("reviews-url");
      $.ajax({
        url: reviewsURL,
        method: "GET",
        data: { game_id: game_id },
        success: function (data) {
          let { reviews } = data;
          renderReviews(reviewsList, reviews);
          container
            .find(".show-hide-button")
            .text(
              reviewsList.is(":visible")
                ? translate("Hide Reviews")
                : translate("Show Reviews")
            );
        },
        error: function () {
          reviewsList.html(translate("Failed to retrieve reviews."));
          reviewsList.show();
        },
      });
    };

    const renderReviews = (reviewsList, reviews) => {
    reviewsList.empty();
    if (reviews.length === 0) {
        reviewsList.html(
            "<p>" +
            translate("There are currently no reviews for this game.") +
            "</p>"
        );
    } else {
        $.each(reviews, function (index, review) {
            let description = review.description.substring(0, 300);
            let truncated = description.length < review.description.length;
            let buttonHtml = truncated
                ? `<button class="read-button-review" data-toggle="read-more">${translate("[Read more...]")}</button>`
                : "";
            let authorName = authorNameTemplate(review);

            let reviewHtml = reviewTemplate(review, authorName, description, truncated, buttonHtml);
            reviewsList.append(reviewHtml);
        });
    }

    const authorNameLinks = document.querySelectorAll(".author-name");
    authorNameLinks.forEach(function(link) {
      link.addEventListener("click", function(event) {
          event.preventDefault();
          const profileUrl = "/users/view_profile/" + this.textContent;
          
          fetch(profileUrl)
              .then(response => {
                  if (!response.ok) {
                      throw new Error("Bad network response.");
                  }
                  const contentType = response.headers.get("content-type");
                  if (contentType && contentType.includes("application/json")) {
                      showMessage($(this).closest(".author-container"), "The user does not exist or has deleted their account.");
                      return;
                  } else {
                      window.open(profileUrl, '_blank');
                  }
              })
              .catch(error => {
                  console.error("There was a problem with the fetch operation:", error);
              });
        });
    });

    reviewsList.show();
};

    const showMessage = (container, message) => {
      let customMessage = $(`<div class="success-message">${message}</div>`);
      container.append(customMessage);

      setTimeout(() => {
        customMessage.fadeOut("slow", function () {
          customMessage.remove();
        });
      }, 3000);
    };

    container
      .on("mouseenter", ".author-container", function () {
        let friendRequestText = $(this).find(".friend-request-text");
        friendRequestText.show();
      })
      .on("mouseleave", ".author-container", function () {
        let friendRequestText = $(this).find(".friend-request-text");
        friendRequestText.hide();
      })
      .on("click", ".friend-request-text", function (e) {
        e.preventDefault();

        if (!isLoggedIn()) {
            showMessage($(this).closest(".author-container"), "Please log in to send friend requests.");
            return;
        }

        let friendReqUrl = $(this)
          .closest(".game-container")
          .data("friend-req");
        let user_id = $(this).closest(".author-link").data("user-id");
        let this_container = $(this).closest(".author-container");

        $.ajax({
          type: "POST",
          url: friendReqUrl,
          headers: {
            "X-CSRFToken": csrfToken,
          },
          data: {
            user_id: user_id,
          },
          success: function (data) {
            console.log(data["message"]);
            showMessage(this_container, data["message"]);
          },
          error: function (error) {
            console.error("Error sending friend request:", error);
            showMessage(this_container, data["message"]);
          },
        });
      });

    const sendRatingAction = (actionType, event) => {
      event.preventDefault();

      let reviewId = $(event.target).closest(".review").data("review-id");
      let ratingUrl = $(event.target)
        .closest(".game-container")
        .data(`${actionType}-url`);
      let this_container = $(event.target).closest(".like-dislike");

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
          showMessage(this_container, data["message"]);
          let likeCountElement = $(event.target)
            .closest(".like-dislike")
            .find(".like-count");
          let dislikeCountElement = $(event.target)
            .closest(".like-dislike")
            .find(".dislike-count");

          likeCountElement.text(data.likes);
          dislikeCountElement.text(data.dislikes);
        },
        error: function (error) {
          console.error(`Error incrementing ${actionType}:`, error);
        },
      });
    }

    container.on("click", ".thumbs-up", function (event) {
      sendRatingAction("like", event);
    });

    container.on("click", ".thumbs-down", function (event) {
      sendRatingAction("dislike", event);
    });

    container.on("click", ".show-hide-button", toggleReviewVisibility);
    container.on("click", ".read-button-review", function () {
      let $description = $(this).parent().find(".review-description");
      let $fullDescription = $(this).parent().find(".review-description-full");
      let buttonText = $(this).text();
      $description.toggle();
      $fullDescription.toggle();
      $(this).text(
        buttonText === translate("[Read more...]")
          ? translate("[Read less...]")
          : translate("[Read more...]")
      );
    });
  });
});

function isLoggedIn() {
    let authenticated = false;
    $.ajax({
        type: "GET",
        url: authCheckUrl,
        async: false,
        success: function(response) {
            authenticated = response.authenticated;
        },
        error: function(xhr, status, error) {
            console.error("Error checking authentication:", error);
        }
    });
    return authenticated;
}