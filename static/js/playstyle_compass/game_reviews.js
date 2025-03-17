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
