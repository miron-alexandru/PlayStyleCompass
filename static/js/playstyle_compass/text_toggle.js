document.querySelectorAll(".overview").forEach(function (truncatedText) {
  let fullText = truncatedText.parentNode.querySelector(".full-text");
  let readButton = truncatedText.parentNode.querySelector(".read-button");

  if (truncatedText.innerHTML === fullText.innerHTML) {
    readButton.style.display = "none";
  }
  else {
    readButton.style.display = "inline";
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


document.querySelectorAll(".games-list").forEach(function (truncatedGames) {
  let fullGames = truncatedGames.parentNode.querySelector(".full-games");
  let readButtonGames = truncatedGames.parentNode.querySelector(".read-button-games");
  
  if (truncatedGames.innerHTML.trim() === fullGames.innerHTML.trim()) {
    readButtonGames.style.display = "none";
    } else {
    readButtonGames.style.display = "inline";
  }
});

function readMoreGames(button) {
  let parent = button.parentNode;
  let gamesList = parent.querySelector(".games-list");
  let fullGames = parent.querySelector(".full-games");

  if (gamesList.style.display === "none") {
    gamesList.style.display = "inline";
    fullGames.style.display = "none";
    button.innerHTML = translate("[Read more...]");
  } else {
    gamesList.style.display = "none";
    fullGames.style.display = "inline";
    button.innerHTML = translate("[Read less...]");
  }
}