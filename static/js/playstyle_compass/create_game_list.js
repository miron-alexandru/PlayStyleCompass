$(document).ready(function () {
  $("#id_games").on("click", "option", function () {
    var $this = $(this);
    $this.prop("selected", !$this.prop("selected"));
    $("#id_games").trigger("change");
  });

  $("#game_search").on("input", function () {
    const searchQuery = this.value.toLowerCase();
    const gameItems = document.querySelectorAll(".game-item");
    let found = false;

    gameItems.forEach(function (item) {
      const gameTitle = item.textContent.toLowerCase();
      if (gameTitle.indexOf(searchQuery) !== -1) {
        item.style.display = "block";
        found = true;
      } else {
        item.style.display = "none";
      }
    });

    const gamesList = document.getElementById("games-list");
    const noResultsMessage = document.getElementById("no-results-message");

    if (!found) {
      if (!noResultsMessage) {
        const message = document.createElement("p");
        message.id = "no-results-message";
        message.textContent = "No games found for your search.";
        message.style.color = "red";
        message.style.textAlign = "center";
        gamesList.appendChild(message);
      }
    } else {
      if (noResultsMessage) {
        noResultsMessage.remove();
      }
    }
  });
});
