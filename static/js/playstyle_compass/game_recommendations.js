document.querySelectorAll(".overview").forEach(function(truncatedText) {
    var fullText = truncatedText.parentNode.querySelector(".full-text");
    var readButton = truncatedText.parentNode.querySelector(".read-button");
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
