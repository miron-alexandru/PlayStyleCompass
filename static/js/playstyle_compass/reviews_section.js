$(document).ready(function() {
    var initialFetch = true;

    function getStarRating(score) {
        var starsHtml = '';
        for (var i = 1; i <= 5; i++) {
            starsHtml += `<i class="fas fa-star ${i <= score ? 'gold-star' : 'empty-star'}"></i>`;
        }
        return starsHtml;
    }

    function pluralizeReviews(count) {
        return count === 1 ? 'review' : 'reviews';
    }

    function toggleReviewVisibility() {
        var reviewsList = $(this).siblings('.reviews-list');
        
        if (initialFetch) {
            // Fetch reviews when the button is clicked for the first time
            fetchReviews.call(this, reviewsList);
            initialFetch = false;
        } else {
            reviewsList.toggle();
        }
        $(this).text(reviewsList.is(':visible') ? 'Hide' : 'Show');
    }

    function fetchReviews(reviewsList) {
        var game_id = $(this).data('game-id');
        var reviewsURL = $('#game-details').data('reviews-url');
        $.ajax({
            url: reviewsURL,
            method: 'GET',
            data: {game_id: game_id},
            success: function(data) {
                var reviews = data.reviews;
                var averageScore = data.average_score;
                renderReviews(reviewsList, reviews);
                $('#average-score').text(averageScore);
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

                var reviewHtml = `
                    <div class="review">
                        <div class="review-header">
                            <p><strong>Author:</strong> ${review.reviewer} - 
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

    function updateAverageScoreStars(averageScore) {
        var starsHtml = getStarRating(averageScore);
        $('#average-score-stars').html(starsHtml);
    }

    function updateTotalReviews(totalReviews) {
        var reviewsText = `${totalReviews} ${pluralizeReviews(totalReviews)}`;
        $('#total-reviews').text(reviewsText);
    }

    var game_id = $(this).data('game-id');
    var averageScoreURL = $('#game-details').data('average-score-url');
    $.ajax({
        url: averageScoreURL,
        method: 'GET',
        data: { game_id: game_id },
        success: function(data) {
            var averageScore = data.average_score;
            var totalReviews = data.total_reviews;
            updateAverageScoreStars(averageScore);
            updateTotalReviews(totalReviews);
        },
        error: function() {
            $('#average-score').text('N/A');
        }
    });

    // Event handlers
    $('.show-hide-button').click(toggleReviewVisibility);
    $(document).on('click', '.read-button-review', function() {
        var $description = $(this).parent().find('.review-description');
        var $fullDescription = $(this).parent().find('.review-description-full');
        var buttonText = $(this).text();
        $description.toggle();
        $fullDescription.toggle();
        $(this).text(buttonText === '[Read more...]' ? '[Read less]' : '[Read more...]');
    });
});