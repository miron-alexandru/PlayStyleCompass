const maxSelections = 3;
const favoriteGenreCheckboxes = document.querySelectorAll('input[name="favorite_genres"]');
const preferredPlatformCheckboxes = document.querySelectorAll('input[name="platforms"]');
const updateButton = document.getElementById('update-button');
const genreWarning = document.getElementById('genre-warning');
const platformWarning = document.getElementById('platform-warning');
const historyWarning = document.getElementById('history-warning');
const gamingHistoryInput = document.getElementById('gaming_history');

function updateCheckboxStates(checkboxes) {
  const selectedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
  checkboxes.forEach(checkbox => {
    checkbox.disabled = selectedCount >= maxSelections && !checkbox.checked;
    });
}

function updateWarnings() {
  const selectedGenres = Array.from(favoriteGenreCheckboxes).filter(cb => cb.checked);
  const selectedPlatforms = Array.from(preferredPlatformCheckboxes).filter(cb => cb.checked);
  const hasSelectedGenres = selectedGenres.length >= 1 && selectedGenres.length <= maxSelections;
  const hasSelectedPlatforms = selectedPlatforms.length >= 1 && selectedPlatforms.length <= maxSelections;
  const hasGamingHistory = gamingHistoryInput.value.trim() !== '';

  genreWarning.style.display = hasSelectedGenres ? 'none' : 'block';
  platformWarning.style.display = hasSelectedPlatforms ? 'none' : 'block';
  historyWarning.style.display = hasGamingHistory ? 'none' : 'block';

  updateButton.disabled = !hasSelectedGenres || !hasSelectedPlatforms || !hasGamingHistory;
}

favoriteGenreCheckboxes.forEach(checkbox => {
  checkbox.addEventListener('change', () => {
    updateCheckboxStates(favoriteGenreCheckboxes);
    updateWarnings();
  });
});

preferredPlatformCheckboxes.forEach(checkbox => {
  checkbox.addEventListener('change', () => {
    updateCheckboxStates(preferredPlatformCheckboxes);
    updateWarnings();
  });
});

gamingHistoryInput.addEventListener('input', () => {
  updateWarnings();
});

updateCheckboxStates(favoriteGenreCheckboxes);
updateCheckboxStates(preferredPlatformCheckboxes);
updateWarnings();