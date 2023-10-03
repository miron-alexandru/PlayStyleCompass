document.addEventListener('DOMContentLoaded', function() {
  const maxSelections = 3;
  const gamingHistoryInput = document.getElementById('gaming_history');
  const historySaveButton = document.getElementById('save-history-button');
  const genresSaveButton = document.getElementById('save-genres-button');
  const platformsSaveButton = document.getElementById('save-platforms-button');
  const saveAllButton = document.getElementById('save-all-button');

  const favoriteGenreCheckboxes = document.querySelectorAll('input[name="favorite_genres"]');
  const favoritePlatformCheckboxes = document.querySelectorAll('input[name="platforms"]');

  function updateSaveButtons() {
    function hasValue(inputElement) {
      return inputElement.value.trim() !== '';
    }

    function hasSelectedCheckboxes(checkboxes, maxSelections) {
      const selectedCheckboxes = Array.from(checkboxes).filter(cb => cb.checked);
      return selectedCheckboxes.length >= 1 && selectedCheckboxes.length <= maxSelections;
    }

    function isAnyCheckboxListEmpty(checkboxLists) {
      return Array.from(checkboxLists).some(checkboxList => {
        return Array.from(checkboxList).every(cb => !cb.checked);
      });
    }

    function isValidGamingHistory(inputElement) {
      const regex = /^[A-Za-z0-9\s]+$/;
      return regex.test(inputElement.value);
    }

    historySaveButton.disabled = !hasValue(gamingHistoryInput) || !isValidGamingHistory(gamingHistoryInput);
    genresSaveButton.disabled = !hasSelectedCheckboxes(favoriteGenreCheckboxes, maxSelections);
    platformsSaveButton.disabled = !hasSelectedCheckboxes(favoritePlatformCheckboxes, maxSelections);
    saveAllButton.disabled = !(
      hasValue(gamingHistoryInput) &&
      isValidGamingHistory(gamingHistoryInput) &&
      hasSelectedCheckboxes(favoriteGenreCheckboxes, maxSelections) &&
      hasSelectedCheckboxes(favoritePlatformCheckboxes, maxSelections) &&
      !isAnyCheckboxListEmpty([favoriteGenreCheckboxes, favoritePlatformCheckboxes])
    );
  }

  function addEventListenerToCheckboxes(checkboxes) {
    checkboxes.forEach(checkbox => {
      checkbox.addEventListener('change', () => {
        updateSaveButtons();
      });
    });
  }

  gamingHistoryInput.addEventListener('input', updateSaveButtons);
  
  addEventListenerToCheckboxes(favoriteGenreCheckboxes);
  addEventListenerToCheckboxes(favoritePlatformCheckboxes);

  updateSaveButtons();
});
