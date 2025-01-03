document.addEventListener("DOMContentLoaded", () => {
  let changesMade = false;
  const maxSelections = 3;
  const singleMaxSelections = 1;
  const gamingHistoryInput = document.getElementById("gaming_history");
  const historySaveButton = document.getElementById("save-history-button");
  const genresSaveButton = document.getElementById("save-genres-button");
  const themesSaveButton = document.getElementById("save-themes-button");
  const platformsSaveButton = document.getElementById("save-platforms-button");
  const gameStylesSaveButton = document.getElementById(
    "save-game-styles-button"
  );
  const connectionTypesSaveButton = document.getElementById(
    "save-connection-types-button"
  );
  const saveAllButton = document.getElementById("save-all-button");

  const favoriteGenreCheckboxes = document.querySelectorAll(
    'input[name="favorite_genres"]'
  );
  const favoritePlatformCheckboxes = document.querySelectorAll(
    'input[name="platforms"]'
  );
  const themesCheckboxes = document.querySelectorAll('input[name="themes"]');
  const gameStylesCheckboxes = document.querySelectorAll(
    'input[name="game_styles"]'
  );
  const connectionTypesCheckboxes = document.querySelectorAll(
    'input[name="connection_types"]'
  );

  const hasValue = (inputElement) => inputElement.value.trim() !== "";

  const hasSelectedCheckboxes = (checkboxes, maxSelections) => {
    const selectedCheckboxes = Array.from(checkboxes).filter(
      (cb) => cb.checked
    );
    return (
      selectedCheckboxes.length >= 1 &&
      selectedCheckboxes.length <= maxSelections
    );
  };

  const isAnyCheckboxListEmpty = (checkboxLists) => {
    return Array.from(checkboxLists).some((checkboxList) => {
      return Array.from(checkboxList).every((cb) => !cb.checked);
    });
  };

  const isValidGamingHistory = (inputElement) => {
    const regex = /^[A-Za-z0-9\s,']+$/;
    return regex.test(inputElement.value);
  };

  const updateSaveButtons = () => {
    historySaveButton.disabled =
      !hasValue(gamingHistoryInput) ||
      !isValidGamingHistory(gamingHistoryInput);

    genresSaveButton.disabled = !hasSelectedCheckboxes(
      favoriteGenreCheckboxes,
      maxSelections
    );

    themesSaveButton.disabled = !hasSelectedCheckboxes(
      themesCheckboxes,
      maxSelections
    );

    platformsSaveButton.disabled = !hasSelectedCheckboxes(
      favoritePlatformCheckboxes,
      maxSelections
    );

    gameStylesSaveButton.disabled = !hasSelectedCheckboxes(
      gameStylesCheckboxes,
      singleMaxSelections
    );

    connectionTypesSaveButton.disabled = !hasSelectedCheckboxes(
      connectionTypesCheckboxes,
      singleMaxSelections
    );

    saveAllButton.disabled =
      !changesMade ||
      !(
        hasValue(gamingHistoryInput) &&
        isValidGamingHistory(gamingHistoryInput) &&
        hasSelectedCheckboxes(favoriteGenreCheckboxes, maxSelections) &&
        hasSelectedCheckboxes(themesCheckboxes, maxSelections) &&
        hasSelectedCheckboxes(favoritePlatformCheckboxes, maxSelections) &&
        hasSelectedCheckboxes(gameStylesCheckboxes, singleMaxSelections) &&
        hasSelectedCheckboxes(connectionTypesCheckboxes, singleMaxSelections) &&
        !isAnyCheckboxListEmpty([
          favoriteGenreCheckboxes,
          themesCheckboxes,
          favoritePlatformCheckboxes,
          gameStylesCheckboxes,
          connectionTypesCheckboxes,
        ])
      );
  };

  const updateSaveButtonTitle = () => {
    if (saveAllButton.disabled) {
      saveAllButton.title = "Update preferences in order to save changes";
    } else {
      saveAllButton.title = "Save all preferences";
    }
  };

  const addEventListenerToCheckboxes = (checkboxes) => {
    checkboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        changesMade = true;
        updateSaveButtons();
        updateSaveButtonTitle();
      });
    });
  };

  gamingHistoryInput.addEventListener("input", () => {
    changesMade = true;
    updateSaveButtons();
    updateSaveButtonTitle();
  });

  addEventListenerToCheckboxes(favoriteGenreCheckboxes);
  addEventListenerToCheckboxes(themesCheckboxes);
  addEventListenerToCheckboxes(favoritePlatformCheckboxes);
  addEventListenerToCheckboxes(gameStylesCheckboxes);
  addEventListenerToCheckboxes(connectionTypesCheckboxes);

  updateSaveButtons();
  updateSaveButtonTitle();
});
