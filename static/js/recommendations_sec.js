function readMore(button) {
  var parent = button.parentNode;
  var dots = parent.querySelector(".dots");
  var moreText = parent.querySelector(".more");

  if (dots.style.display === "none") {
    dots.style.display = "inline";
    button.innerHTML = "[Read more...]";
    moreText.style.display = "none";
  } else {
    dots.style.display = "none";
    button.innerHTML = "[Read less...]";
    moreText.style.display = "inline";
  }
}