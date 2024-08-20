const maxSelections = 3;
const favoriteGenreCheckboxes = document.querySelectorAll(
  'input[name="favorite_genres"]'
);
const preferredPlatformCheckboxes = document.querySelectorAll(
  'input[name="platforms"]'
);
const themesCheckboxes = document.querySelectorAll(
  'input[name="themes"]'
);

const gamingHistoryInput = document.getElementById("gaming_history");
const updateButton = document.getElementById("update-button");
const genreWarning = document.getElementById("genre-warning");
const themeWarning = document.getElementById('theme-warning');
const platformWarning = document.getElementById("platform-warning");
const historyWarning = document.getElementById("history-warning");

function updateCheckboxStates(checkboxes) {
  const selectedCount = Array.from(checkboxes).filter(
    (cb) => cb.checked
  ).length;
  checkboxes.forEach((checkbox) => {
    checkbox.disabled = selectedCount >= maxSelections && !checkbox.checked;
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

  const hasSelectedGenres =
    selectedGenres.length >= 1 && selectedGenres.length <= maxSelections;
  const hasSelectedThemes = 
    selectedThemes.length >= 1 && selectedGenres.length <= maxSelections;
  const hasSelectedPlatforms =
    selectedPlatforms.length >= 1 && selectedPlatforms.length <= maxSelections;
  const hasGamingHistory = gamingHistoryInput.value.trim() !== "";

  genreWarning.style.display = hasSelectedGenres ? "none" : "block";
  platformWarning.style.display = hasSelectedPlatforms ? "none" : "block";
  themeWarning.style.display = hasSelectedThemes ? "none" : "block";
  historyWarning.style.display = hasGamingHistory ? "none" : "block";

  updateButton.disabled =
    !hasSelectedGenres || !hasSelectedThemes || !hasSelectedPlatforms || !hasGamingHistory;
}

favoriteGenreCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    updateCheckboxStates(favoriteGenreCheckboxes);
    updateWarnings();
  });
});

themesCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    updateCheckboxStates(themesCheckboxes);
    updateWarnings();
  });
});

preferredPlatformCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    updateCheckboxStates(preferredPlatformCheckboxes);
    updateWarnings();
  });
});

gamingHistoryInput.addEventListener("input", () => {
  updateWarnings();
});

updateCheckboxStates(favoriteGenreCheckboxes);
updateCheckboxStates(themesCheckboxes);
updateCheckboxStates(preferredPlatformCheckboxes);
updateWarnings();
