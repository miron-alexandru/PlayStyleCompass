$(document).ready(function() {
    $('.game-container').each(function() {
        var container = $(this);

        var initialFetch = true;

        function getStarRating(score) {
            var starsHtml = '';
            for (var i = 1; i <= 5; i++) {
                starsHtml += `<i class="fas fa-star ${i <= score ? 'gold-star' : 'empty-star'}"></i>`;
            }
            return starsHtml;
        }

        function toggleReviewVisibility() {
            var reviewsList = container.find('.reviews-list');

            if (initialFetch) {
                fetchReviews.call(this, reviewsList);
                initialFetch = false;
            } else {
                reviewsList.toggle();
            }
            container.find('.show-hide-button').text(reviewsList.is(':visible') ? 'Hide Reviews' : 'Show Reviews');
        }

        function fetchReviews(reviewsList) {
            var game_id = container.data('game-id');
            var reviewsURL = container.data('reviews-url');
            $.ajax({
                url: reviewsURL,
                method: 'GET',
                data: { game_id: game_id },
                success: function(data) {
                    var reviews = data.reviews;
                    renderReviews(reviewsList, reviews);
                    container.find('.show-hide-button').text(reviewsList.is(':visible') ? 'Hide Reviews' : 'Show Reviews');
                },
                error: function() {
                    reviewsList.html('Failed to retrieve reviews.');
                    reviewsList.show();
                }
            });
        }

        function renderReviews(reviewsList, reviews) {
          reviewsList.empty();
          if (reviews.length === 0) {
              reviewsList.html('<p><strong>No reviews for this game yet.</strong></p>');
          } else {
              $.each(reviews, function(index, review) {
                  var description = review.description.substring(0, 300);
                  var truncated = description.length < review.description.length;
                  var buttonHtml = truncated ? `<button class="read-button-review" data-toggle="read-more">[Read more...]</button>` : '';
                  var authorName = `<span class="author-container">
                            <span class="author-name">${review.reviewer}</span>
                            <a href="#" class="author-link" data-user-id="${review.user_id}">
                                <span class="friend-request-text" style="display: none;">Friend Request</span>
                            </a>
                        </span>`;

                  var reviewHtml = `
                      <div class="review">
                          <div class="review-header">
                              <p><strong>Author:</strong> ${authorName} - 
                                  <span class="star-rating">${getStarRating(review.score)}</span>
                              </p>
                              <p><strong>Title:</strong> ${review.title}</p>
                          </div>
                          <div class="review-body">
                              <p><strong>Summary:</strong></p>
                              <div class="review-description-container">
                                  <span class="review-description" data-full-description="${review.description}">${description}</span>
                                  <span class="review-description-full" style="display: none;">${review.description}</span>
                              </div>
                              ${buttonHtml}
                          </div>
                          <div class="review-footer">
                              <p><strong>Rating:</strong> ${review.score}</p>
                          </div>
                      </div>
                  `;
                  reviewsList.append(reviewHtml);
              });
          }
          reviewsList.show();
      }

        function showMessage(container, message) {
            var customMessage = $(`<div class="success-message">${message}</div>`);
            container.append(customMessage);

            setTimeout(function () {
                customMessage.fadeOut('slow', function () {
                    customMessage.remove();
                });
            }, 3000);
        }

        container.on('mouseenter', '.author-container', function () {
            var friendRequestText = $(this).find('.friend-request-text');
            friendRequestText.show();
        }).on('mouseleave', '.author-container', function () {
            var friendRequestText = $(this).find('.friend-request-text');
            friendRequestText.hide();
        }).on('click', '.friend-request-text', function (e) {
            event.preventDefault();

            var friendReqUrl = $(this).closest('.game-container').data('friend-req');
            var csrfToken = document.cookie.match(/csrftoken=([^ ;]+)/)[1];
            var user_id = $(this).closest('.author-link').data('user-id');
            var this_container = $(this).closest('.author-container')

            $.ajax({
                type: 'POST',
                url: friendReqUrl,
                headers: {
                'X-CSRFToken': csrfToken
                },
                data: {
                "user_id": user_id,
                },
                success: function(data) {
                        console.log('Friend request sent successfully!');
                        showMessage(this_container, data['message']);
                    },
                error: function(error) {
                        console.error('Error sending friend request:', error);
                        showMessage(this_container, data['message']);
                }
            }); 
        });

        container.on('click', '.show-hide-button', toggleReviewVisibility);
        container.on('click', '.read-button-review', function() {
            var $description = $(this).parent().find('.review-description');
            var $fullDescription = $(this).parent().find('.review-description-full');
            var buttonText = $(this).text();
            $description.toggle();
            $fullDescription.toggle();
            $(this).text(buttonText === '[Read more...]' ? '[Read less]' : '[Read more...]');
        });
    });
});