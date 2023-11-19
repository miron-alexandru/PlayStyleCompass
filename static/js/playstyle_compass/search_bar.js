const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

searchInput.addEventListener('input', function() {
  const query = searchInput.value.trim();

  if (query === '') {
    searchResults.innerHTML = '';
    return;
  }

  fetch(`/autocomplete/?query=${query}`)
    .then(response => response.json())
    .then(data => {
      let resultsHTML = '';
      data.forEach(result => {
        resultsHTML += `<div class="result" onclick="fillSearchBar('${result.title}')">${result.title}</div>`;
      });
      searchResults.innerHTML = resultsHTML;
    });
});

function fillSearchBar(value) {
  searchInput.value = decodeURIComponent(value); // Decode the encoded value
  searchResults.innerHTML = '';
  document.querySelector('.search-form').submit();
}

searchResults.addEventListener('click', function (event) {
  const {target} = event;
  if (target.classList.contains('result')) {
    const clickedTitle = target.textContent;
    fillSearchBar(clickedTitle);
  }
});

function validateSearch() {
    const searchInput = document.getElementById('search-input');
    const query = searchInput.value.trim();

    if (query === '') {
      return false;
    }

    return true;
  }