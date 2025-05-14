const getStarRating = (score) => {
  let starsHtml = "";
  for (let i = 1; i <= 5; i++) {
    starsHtml += `<i class="fas fa-star ${
      i <= score ? "gold-star" : "empty-star"
    }"></i>`;
  }
  return starsHtml;
};

const reviewTemplate = (
  review,
  authorName,
  description,
  truncated,
  buttonHtml
) => `
    <div class="review" data-review-id="${review.id}">
        <div class="review-header">
            <div class="like-dislike">
                <i class="fa-solid fa-thumbs-up thumbs-up" title="${translate(
                  "I like this"
                )}"></i><span class="like-count">${review.likes}</span>
                <span class="like-dislike-divider">|</span>
                <i class="fa-solid fa-thumbs-down thumbs-down" title="${translate(
                  "I dislike this"
                )}"></i><span class="dislike-count">${review.dislikes}</span>
                  <span class="like-dislike-divider">|</span>
                <a href="/share-review/${review.id}/" class="share-button" title="${translate('Share with friends')}" target="_blank" rel="noopener noreferrer">
                  <i class="fa-solid fa-share"></i>
                </a>
            </div>
            <div class="review-score">
            <p><span>${getStarRating(review.score)}</span></p>
            </div>
            <p class="review-title">${review.title}</p>
            <div class="game-review-details">
            <p>${translate("Written by")} ${authorName} on ${review.date_added}</p>
            </div>
        </div>
        <div class="review-body">
            <div class="review-description-container">
                <span class="review-description" data-full-description="${
                  review.description
                }">${description}</span>
                <span class="review-description-full" style="display: none;">${
                  review.description
                }</span>
            </div>
            ${buttonHtml}
        </div>
    </div>
`;

const authorNameTemplate = (review) => `
    <span class="author-container">
        <span class="author-name" title="Open user profile in a new tab.">${
          review.reviewer
        }</span>
        <a href="#" class="author-link" data-user-id="${review.user_id}">
            <span class="friend-request-text" style="display: none;">${translate(
              "Friend Request"
            )}</span>
        </a>
    </span>
`;
