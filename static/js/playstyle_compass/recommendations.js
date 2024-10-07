document.addEventListener("DOMContentLoaded", () => {
  const hideAllContainers = () => {
    const gameContainers = document.querySelectorAll(
      ".game-recommendations-container"
    );
    gameContainers.forEach((container) => {
      container.style.display = "none";
    });
  };

  const showCategoryContainer = (category) => {
    const selectedContainer = document.querySelector(`.${category}`);
    if (selectedContainer) {
      selectedContainer.style.display = "block";
    }
  };

  const getCategoryAndPageFromURL = () => {
    const searchParams = new URLSearchParams(window.location.search);
    const category = searchParams.get("category") || "playstyle_games";
    const page = searchParams.get("page") || 1;
    const sort = searchParams.get("sort") || "recommended";
    return {
      category,
      page,
      sort,
    };
  };

  const { category, page, sort } = getCategoryAndPageFromURL();
  hideAllContainers();
  showCategoryContainer(category);

  const sortSelect = document.getElementById("sort-select");
  sortSelect.value = sort;

  sortSelect.addEventListener("change", () => {
    const selectedCategory = getCategoryAndPageFromURL().category;
    const selectedSortOption = sortSelect.value;

    const newUrl = `?category=${selectedCategory}&sort=${selectedSortOption}&page=${page}`;
    window.location.href = newUrl;
  });

  const buttons = document.querySelectorAll(".category-button");
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const selectedCategory = button.dataset.category;
      const newUrl = `?category=${selectedCategory}&sort=${sort}&page=1`;

      window.location.href = newUrl;

      const onUrlChange = () => {
        hideAllContainers();
        showCategoryContainer(selectedCategory);

        window.removeEventListener("popstate", onUrlChange);
      };

      window.addEventListener("popstate", onUrlChange);
    });
  });

  window.addEventListener("popstate", (event) => {
    const { category, page, sort } = getCategoryAndPageFromURL();
    hideAllContainers();
    showCategoryContainer(category);

    sortSelect.value = sort;
  });
});
