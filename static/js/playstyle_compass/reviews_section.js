$(document).ready(function() {
    $('.game-container').each(function() {
        let container = $(this);

        let initialFetch = true;

        const getStarRating = (score) => {
            let starsHtml = '';
            for (let i = 1; i <= 5; i++) {
                starsHtml += `<i class="fas fa-star ${i <= score ? 'gold-star' : 'empty-star'}"></i>`;
            }
            return starsHtml;
        };

        const toggleReviewVisibility = () => {
            let reviewsList = container.find('.reviews-list');

            if (initialFetch) {
                fetchReviews.call(this, reviewsList);
                initialFetch = false;
            } else {
                reviewsList.toggle();
            }
            container.find('.show-hide-button').text(reviewsList.is(':visible') ? 'Hide Reviews' : 'Show Reviews');
        };

        const fetchReviews = (reviewsList) => {
            let game_id = container.data('game-id');
            let reviewsURL = container.data('reviews-url');
            $.ajax({
                url: reviewsURL,
                method: 'GET',
                data: { game_id: game_id },
                success: function(data) {
                    let {reviews} = data;
                    renderReviews(reviewsList, reviews);
                    container.find('.show-hide-button').text(reviewsList.is(':visible') ? 'Hide Reviews' : 'Show Reviews');
                },
                error: function() {
                    reviewsList.html('Failed to retrieve reviews.');
                    reviewsList.show();
                }
            });
        };

        const renderReviews = (reviewsList, reviews) => {
            reviewsList.empty();
            if (reviews.length === 0) {
                reviewsList.html('<p><strong>No reviews for this game yet.</strong></p>');
            } else {
                $.each(reviews, function(index, review) {
                    let description = review.description.substring(0, 300);
                    let truncated = description.length < review.description.length;
                    let buttonHtml = truncated ? `<button class="read-button-review" data-toggle="read-more">[Read more...]</button>` : '';
                    let authorName = `<span class="author-container">
                                <span class="author-name" data-profile-name="${review.reviewer}">${review.reviewer}</span>
                                <a href="#" class="author-link" data-user-id="${review.user_id}">
                                    <span class="friend-request-text" style="display: none;">Friend Request</span>
                                </a>
                            </span>`;

                    let reviewHtml = `
                        <div class="review" data-review-id="${review.id}">
                            <div class="review-header">
                            <div class="like-dislike">
                                <i class="fa-solid fa-thumbs-up thumbs-up"></i><span class="like-count">${review.likes}</span>
                                <span class="like-dislike-divider">|</span>
                                <i class="fa-solid fa-thumbs-down thumbs-down"></i><span class="dislike-count">${review.dislikes}</span>
                            </div>
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
        };

        const showMessage = (container, message) => {
            let customMessage = $(`<div class="success-message">${message}</div>`);
            container.append(customMessage);

            setTimeout(() => {
                customMessage.fadeOut('slow', function () {
                    customMessage.remove();
                });
            }, 3000);
        };

        container.on('mouseenter', '.author-container', function () {
            let friendRequestText = $(this).find('.friend-request-text');
            friendRequestText.show();
        }).on('mouseleave', '.author-container', function () {
            let friendRequestText = $(this).find('.friend-request-text');
            friendRequestText.hide();
        }).on('click', '.friend-request-text', function (e) {
            e.preventDefault();

            let friendReqUrl = $(this).closest('.game-container').data('friend-req');
            let csrfToken = document.cookie.match(/csrftoken=([^ ;]+)/)[1];
            let user_id = $(this).closest('.author-link').data('user-id');
            let this_container = $(this).closest('.author-container');

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
                    console.log(data['message']);
                    showMessage(this_container, data['message']);
                },
                error: function(error) {
                    console.error('Error sending friend request:', error);
                    showMessage(this_container, data['message']);
                }
            });
        });


        container.on('click', '.author-name', function () {
            let profileName = $(this).closest('.author-name').data('profile-name');
            let this_container = $(this).closest('.author-container');

            if (profileName) {
                userProfileUrl = '/users/view_profile/' + profileName
                window.location.href = userProfileUrl;
            }
        });


        function sendRatingAction(actionType, event) {
            event.preventDefault();

            let csrfToken = document.cookie.match(/csrftoken=([^ ;]+)/)[1];
            let reviewId = $(event.target).closest('.review').data('review-id');
            let ratingUrl = $(event.target).closest('.game-container').data(`${actionType}-url`);
            let this_container = $(event.target).closest('.like-dislike');

            $.ajax({
                type: 'POST',
                url: ratingUrl,
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                data: {
                    "review_id": reviewId,
                },
                success: function (data) {
                    showMessage(this_container, data['message']);
                    let likeCountElement = $(event.target).closest('.like-dislike').find('.like-count');
                    let dislikeCountElement = $(event.target).closest('.like-dislike').find('.dislike-count');

                    if (actionType === 'like') {
                        likeCountElement.text(data.likes);
                    } else if (actionType === 'dislike') {
                        dislikeCountElement.text(data.dislikes);
                    }
                },
                error: function (error) {
                    console.error(`Error incrementing ${actionType}:`, error);
                }
            });
        }

        container.on('click', '.thumbs-up', function (event) {
            sendRatingAction('like', event);
        });

        container.on('click', '.thumbs-down', function (event) {
            sendRatingAction('dislike', event);
        });

        container.on('click', '.show-hide-button', toggleReviewVisibility);
        container.on('click', '.read-button-review', function() {
            let $description = $(this).parent().find('.review-description');
            let $fullDescription = $(this).parent().find('.review-description-full');
            let buttonText = $(this).text();
            $description.toggle();
            $fullDescription.toggle();
            $(this).text(buttonText === '[Read more...]' ? '[Read less]' : '[Read more...]');
        });
    });
});
