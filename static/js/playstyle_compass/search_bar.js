const searchInput = document.getElementById("search-input");
const searchResults = document.getElementById("search-results");
const searchTypeRadios = document.getElementsByName("search_type");
const searchForm = document.querySelector(".search-form");

searchInput.addEventListener("input", function () {
  const query = searchInput.value.trim();

  if (query === "") {
    searchResults.innerHTML = "";
    return;
  }

  const searchType = getSelectedSearchType();
  const autocompleteUrl = `/autocomplete/${searchType}/?query=${query}`;

  fetch(autocompleteUrl)
    .then((response) => response.json())
    .then((data) => {
      let resultsHTML = "";
      data.forEach((result) => {
        resultsHTML += `<div class="result" onclick="fillSearchBar('${result.title}')">${result.title}</div>`;
      });
      searchResults.innerHTML = resultsHTML;
    });
});

document
  .getElementById("search-form")
  .addEventListener("submit", function (event) {
    let searchType = document.querySelector(
      'input[name="search_type"]:checked'
    ).value;

    if (searchType === "games") {
      this.action = searchGames;
    } else if (searchType === "franchises") {
      this.action = searchFranchises;
    }
  });

function fillSearchBar(value) {
  searchInput.value = decodeURIComponent(value);
  const searchType = getSelectedSearchType();

  if (searchType === "games") {
    searchForm.action = searchGames;
  } else if (searchType === "franchises") {
    searchForm.action = searchFranchises;
  }

  searchResults.innerHTML = "";
  searchForm.submit();
}

searchResults.addEventListener("click", function (event) {
  const { target } = event;
  if (target.classList.contains("result")) {
    const clickedTitle = target.textContent;
    fillSearchBar(clickedTitle);
  }
});

function validateSearch() {
  const searchInput = document.getElementById("search-input");
  const query = searchInput.value.trim();

  if (query === "") {
    return false;
  }

  return true;
}

function getSelectedSearchType() {
  for (const radio of searchTypeRadios) {
    if (radio.checked) {
      return radio.value;
    }
  }

  return "games";
}
