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
      const sort = searchParams.get('sort') || 'recommended';
      return {
        category,
        page,
        sort
      };
    }

    const {
      category,
      page,
      sort
    } = getCategoryAndPageFromURL();
    hideAllContainers();
    showCategoryContainer(category);

    // Update the select element with the current sort option
    const sortSelect = document.getElementById('sort-select');
    sortSelect.value = sort;

    // Handle sorting when the select element changes
    sortSelect.addEventListener('change', () => {
      const selectedCategory = getCategoryAndPageFromURL().category;
      const selectedSortOption = sortSelect.value;

      // Update the URL with the new sort parameter and reload the page
      const newUrl = `?category=${selectedCategory}&sort=${selectedSortOption}`;
      window.location.href = newUrl;
    });

    const buttons = document.querySelectorAll('.category-button');
    buttons.forEach(button => {
      button.addEventListener('click', () => {
        const selectedCategory = button.dataset.category;
        hideAllContainers();
        showCategoryContainer(selectedCategory);

        // Update the URL with the new category parameter without reloading the page
        const newUrl = `?category=${selectedCategory}&sort=${sort}`;
        history.pushState(null, null, newUrl);
      });
    });

    window.addEventListener('popstate', (event) => {
      const {
        category,
        page,
        sort
      } = getCategoryAndPageFromURL();
      hideAllContainers();
      showCategoryContainer(category);

      sortSelect.value = sort;
    });
  });