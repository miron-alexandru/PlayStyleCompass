function filterGames(category) {
    const gameContainers = document.querySelectorAll('.game-recommendations-container');

    gameContainers.forEach(container => {
      container.style.display = 'none';
    });

    const selectedContainer = document.querySelector(`.${category}`);
    if (selectedContainer) {
      selectedContainer.style.display = 'block';
    }
  }

  const buttons = document.querySelectorAll('.category-button');
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      filterGames(button.dataset.category);
    });
  });