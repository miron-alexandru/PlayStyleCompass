function fillStars(score, maxScore) {
  let stars = '';
  for (let i = 1; i <= maxScore; i++) {
    if (i <= score) {
      stars += '<i class="fas fa-star gold-star"></i>';
    } else {
      stars += '<i class="far fa-star empty-star"></i>';
    }
  }
  return stars;
}

document.addEventListener("DOMContentLoaded", function() {
  const starRatingElements = document.querySelectorAll(".star-rating");
  starRatingElements.forEach(function(element) {
    const scoreElement = element.querySelector(".score-hidden");
    const score = parseInt(scoreElement.textContent);
    const maxScore = 5;
    const stars = fillStars(score, maxScore);
    element.innerHTML = stars;
    scoreElement.style.display = "inline";
  });
});

function toggleReviews(button) {
  const reviewsSection = button.parentElement.nextElementSibling;
  if (reviewsSection.style.display === "none" || reviewsSection.style.display === "") {
    reviewsSection.style.display = "block";
    button.textContent = "Hide";
  } else {
    reviewsSection.style.display = "none";
    button.textContent = "Show";
  }
}
