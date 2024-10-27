document.addEventListener("DOMContentLoaded", function () {
  const filterForm = document.getElementById("filterForm");

  function removeEmptyFields() {
    const elements = filterForm.elements;

    for (let i = elements.length - 1; i >= 0; i--) {
      if (elements[i].name && elements[i].value === "") {
        elements[i].parentNode.removeChild(elements[i]);
      }
    }
  }

  filterForm.addEventListener("submit", function (event) {
    removeEmptyFields();
  });

  document.getElementById("resetButton").addEventListener("click", function () {
    const selects = document.querySelectorAll(".filter-container select");

    selects.forEach(function (select) {
      select.value = "";
    });

    removeEmptyFields();
    filterForm.submit();
  });

  function handleSubmitForm() {
    removeEmptyFields();
    filterForm.submit();
  }

  document
    .getElementById("filter_by")
    .addEventListener("change", handleSubmitForm);
  document
    .getElementById("sort_by")
    .addEventListener("change", handleSubmitForm);
});
