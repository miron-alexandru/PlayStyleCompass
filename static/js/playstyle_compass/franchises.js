document.querySelectorAll(".overview").forEach(function (truncatedText) {
  let fullText = truncatedText.parentNode.querySelector(".full-text");
  let readButton = truncatedText.parentNode.querySelector(".read-button");
  if (truncatedText.innerHTML === fullText.innerHTML) {
    readButton.style.display = "none";
  }
});


function readMore(button) {
  let parent = button.parentNode;
  let truncatedText = parent.querySelector(".overview");
  let fullText = parent.querySelector(".full-text");

  if (truncatedText.style.display === "none") {
    truncatedText.style.display = "inline";
    fullText.style.display = "none";
    button.innerHTML = translate("[Read more...]");
  } else {
    truncatedText.style.display = "none";
    fullText.style.display = "inline";
    button.innerHTML = translate("[Read less...]");
  }
}
