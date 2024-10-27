const searchInput = document.getElementById("search-input");
const searchResults = document.getElementById("search-results");
const searchTypeRadios = document.getElementsByName("search_type");
const searchForm = document.querySelector(".search-form");
let currentSearchType = getSelectedSearchType();

searchInput.addEventListener("input", function () {
  const query = searchInput.value.trim();

  if (query === "") {
    searchResults.innerHTML = "";
    searchResults.style.display = "none";
    return;
  }

  const searchType = currentSearchType;
  const autocompleteUrl = `/autocomplete/${searchType}/?query=${query}`;

  fetch(autocompleteUrl)
    .then((response) => response.json())
    .then((data) => {
      let resultsHTML = "";
      data.results.forEach((result) => {
        let titleOrName = "";
        if (searchType === "characters") {
          titleOrName = result.name;
        } else {
          titleOrName = result.title;
        }
        resultsHTML += `<div class="result" onclick="fillSearchBar('${titleOrName}')">${titleOrName}</div>`;
      });

      searchResults.innerHTML = resultsHTML;
      searchResults.style.display = data.results.length > 0 ? "block" : "none";
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
    } else if (searchType === "characters") {
      this.action = searchCharacters;
    }
  });

document
  .querySelectorAll('input[name="search_type"]')
  .forEach(function (radio) {
    radio.addEventListener("change", function () {
      currentSearchType = getSelectedSearchType();
      searchInput.dispatchEvent(new Event("input"));
    });
  });

function fillSearchBar(value) {
  searchInput.value = decodeURIComponent(value);
  const searchType = getSelectedSearchType();

  if (searchType === "games") {
    searchForm.action = searchGames;
  } else if (searchType === "franchises") {
    searchForm.action = searchFranchises;
  } else if (searchType === "characters") {
    searchForm.action = searchCharacters;
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

  if (query.length < 2) {
    alert("Please enter at least 2 characters for your search.");
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
