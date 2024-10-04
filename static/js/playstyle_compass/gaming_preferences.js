const maxSelections = 3;
const singularSelections = 1;
const favoriteGenreCheckboxes = document.querySelectorAll(
  'input[name="favorite_genres"]'
);
const preferredPlatformCheckboxes = document.querySelectorAll(
  'input[name="platforms"]'
);
const themesCheckboxes = document.querySelectorAll(
  'input[name="themes"]'
);
const connectionsCheckboxes = document.querySelectorAll(
  'input[name="connection_types"]'
);
const stylesCheckboxes = document.querySelectorAll(
  'input[name="game_styles"]'
);

const gamingHistoryInput = document.getElementById("gaming_history");
const updateButton = document.getElementById("update-button");
const genreWarning = document.getElementById("genre-warning");
const themeWarning = document.getElementById('theme-warning');
const platformWarning = document.getElementById("platform-warning");
const historyWarning = document.getElementById("history-warning");
const connectionWarning = document.getElementById("connection-warning");
const styleWarning = document.getElementById("style-warning");

function updateCheckboxStates(checkboxes, selections) {
  const selectedCount = Array.from(checkboxes).filter(
    (cb) => cb.checked
  ).length;
  checkboxes.forEach((checkbox) => {
    checkbox.disabled = selectedCount >= selections && !checkbox.checked;
  });
}

function updateWarnings() {
  const selectedGenres = Array.from(favoriteGenreCheckboxes).filter(
    (cb) => cb.checked
  );
  const selectedPlatforms = Array.from(preferredPlatformCheckboxes).filter(
    (cb) => cb.checked
  );
  const selectedThemes = Array.from(themesCheckboxes).filter(
    (cb) => cb.checked
  );
  const selectedConnections = Array.from(connectionsCheckboxes).filter(
    (cb) => cb.checked
  );
  const selectedStyles = Array.from(stylesCheckboxes).filter(
    (cb) => cb.checked
  );


  const hasSelectedGenres =
    selectedGenres.length >= 1 && selectedGenres.length <= maxSelections;
  const hasSelectedThemes = 
    selectedThemes.length >= 1 && selectedGenres.length <= maxSelections;
  const hasSelectedPlatforms =
    selectedPlatforms.length >= 1 && selectedPlatforms.length <= maxSelections;
  const hasSelectedConnections =
    selectedConnections.length >= 1 && selectedConnections.length <= singularSelections;
  const hasSelectedStyles =
    selectedStyles.length >= 1 && selectedStyles.length <= singularSelections;
  const hasGamingHistory = gamingHistoryInput.value.trim() !== "";

  genreWarning.style.display = hasSelectedGenres ? "none" : "block";
  platformWarning.style.display = hasSelectedPlatforms ? "none" : "block";
  themeWarning.style.display = hasSelectedThemes ? "none" : "block";
  historyWarning.style.display = hasGamingHistory ? "none" : "block";
  connectionWarning.style.display = hasSelectedConnections ? "none" : "block";
  styleWarning.style.display = hasSelectedStyles ? "none" : "block";

  updateButton.disabled =
    !hasSelectedGenres || !hasSelectedThemes || !hasSelectedPlatforms || !hasGamingHistory || !hasSelectedConnections || !hasSelectedStyles;
}

favoriteGenreCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    updateCheckboxStates(favoriteGenreCheckboxes, maxSelections);
    updateWarnings();
  });
});

themesCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    updateCheckboxStates(themesCheckboxes, maxSelections);
    updateWarnings();
  });
});

preferredPlatformCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    updateCheckboxStates(preferredPlatformCheckboxes, maxSelections);
    updateWarnings();
  });
});

connectionsCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    updateCheckboxStates(connectionsCheckboxes, singularSelections);
    updateWarnings();
  });
});

stylesCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    updateCheckboxStates(stylesCheckboxes, singularSelections);
    updateWarnings();
  });
});

gamingHistoryInput.addEventListener("input", () => {
  updateWarnings();
});

updateCheckboxStates(favoriteGenreCheckboxes, maxSelections);
updateCheckboxStates(themesCheckboxes, maxSelections);
updateCheckboxStates(preferredPlatformCheckboxes, maxSelections);
updateCheckboxStates(connectionsCheckboxes, singularSelections);
updateCheckboxStates(stylesCheckboxes, singularSelections);
updateWarnings();
