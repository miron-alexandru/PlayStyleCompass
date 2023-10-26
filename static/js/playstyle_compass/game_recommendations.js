document.querySelectorAll(".overview").forEach(function(truncatedText) {
    var fullText = truncatedText.parentNode.querySelector(".full-text");
    var readButton = truncatedText.parentNode.querySelector(".read-button");
    if (truncatedText.innerHTML === fullText.innerHTML) {
      readButton.style.display = "none";
    }
  });

document.querySelectorAll(".review").forEach(function (review) {
    var truncatedText = review.querySelector(".review-description");
    var fullText = review.querySelector(".review-description-full");
    var readButton = review.querySelector(".read-button-review");
    if (truncatedText.innerHTML === fullText.innerHTML) {
      readButton.style.display = "none";
    }
});

  function readMore(button) {
    var parent = button.parentNode;
    var truncatedText = parent.querySelector(".overview");
    var fullText = parent.querySelector(".full-text");

    if (truncatedText.style.display === "none") {
      truncatedText.style.display = "inline";
      fullText.style.display = "none";
      button.innerHTML = "[Read more...]";
    } else {
      truncatedText.style.display = "none";
      fullText.style.display = "inline";
      button.innerHTML = "[Read less...]";
    }
  }

  function readMoreReview(button) {
    var parent = button.parentNode;
    var truncatedText = parent.querySelector(".review-description");
    var fullText = parent.querySelector(".review-description-full");

    if (truncatedText.style.display === "none") {
      truncatedText.style.display = "inline";
      fullText.style.display = "none";
      button.innerHTML = "[Read more...]";
    } else {
      truncatedText.style.display = "none";
      fullText.style.display = "inline";
      button.innerHTML = "[Read less...]";
    }
  }
