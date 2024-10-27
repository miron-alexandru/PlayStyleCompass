document.addEventListener("DOMContentLoaded", () => {
  const genres = $(".form-container")
    .data("gaming-genres")
    .split(",")
    .map((g) => g.trim());
  const gameModes = $(".form-container")
    .data("favorite-game-modes")
    .split(",")
    .map((g) => g.trim());

  const checkCheckboxes = (items) => {
    items.forEach((item) => {
      const checkbox = document.querySelector(
        `input[type="checkbox"][value="${item}"]`
      );
      if (checkbox) checkbox.checked = true;
    });
  };

  checkCheckboxes(genres);
  checkCheckboxes(gameModes);
});

$(document).ready(() => {
  const toggleCheckboxes = (name) => {
    const checkedCount = $(`input[name="${name}"]:checked`).length;
    const checkboxes = $(`input[name="${name}"]`).not(":checked");

    checkboxes.prop("disabled", checkedCount >= 3);
  };

  const initToggle = (name) => {
    toggleCheckboxes(name);
    $(`input[name="${name}"]`).on("change", () => toggleCheckboxes(name));
  };

  initToggle("gaming_genres");
  initToggle("favorite_game_modes");
});
