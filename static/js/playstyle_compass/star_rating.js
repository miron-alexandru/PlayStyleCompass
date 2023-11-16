function fillStars(score, maxScore, starContainer) {
  let stars = '';
  for (let i = 1; i <= maxScore; i++) {
    if (i <= score) {
      stars += '<i class="fas fa-star gold-star"></i>';
    } else {
      stars += '<i class="far fa-star empty-star"></i>';
    }
  }
  starContainer.innerHTML = stars;
  starContainer.style.display = 'inline';
}

document.addEventListener('DOMContentLoaded', function () {
  const starRatingElements = document.querySelectorAll('.star-rating');
  starRatingElements.forEach(function (element) {
    const scoreElement = element.querySelector('.score-hidden');

    if (scoreElement) {
      const score = parseInt(scoreElement.textContent);
      const maxScore = 5;
      fillStars(score, maxScore, element);
    }
  });
});
