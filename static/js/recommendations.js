document.addEventListener("DOMContentLoaded", function() {
  function hideAllContainers() {
    const gameContainers = document.querySelectorAll('.game-recommendations-container');
    gameContainers.forEach(container => {
      container.style.display = 'none';
    });
  }

  function showCategoryContainer(category) {
    const selectedContainer = document.querySelector(`.${category}`);
    if (selectedContainer) {
      selectedContainer.style.display = 'block';
    }
  }

  function getCategoryAndPageFromURL() {
    const searchParams = new URLSearchParams(window.location.search);
    const category = searchParams.get('category') || 'gaming_history';
    const page = searchParams.get(`${category}_page`) || 1;
    return {
      category,
      page
    };
  }

  const {
    category,
    page
  } = getCategoryAndPageFromURL();
  hideAllContainers();
  showCategoryContainer(category);

  const buttons = document.querySelectorAll('.category-button');
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const selectedCategory = button.dataset.category;
      hideAllContainers();
      showCategoryContainer(selectedCategory);

      // Update the URL without page reload
      const newUrl = `?category=${selectedCategory}`;
      history.pushState(null, null, newUrl);
    });
  });

  window.addEventListener('popstate', (event) => {
    const {
      category,
      page
    } = getCategoryAndPageFromURL();
    hideAllContainers();
    showCategoryContainer(category);
  });
});
