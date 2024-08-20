document.addEventListener("DOMContentLoaded", function () {
  const maxSelections = 3;
  const changeButtons = document.querySelectorAll(".change-button");
  const saveButtons = document.querySelectorAll(".save-button");

  changeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const section = this.getAttribute("data-section");
      const form = document.getElementById(section + "-form");
      const saveButton = document.querySelector(
        `.save-button[data-section="${section}"]`
      );

      if (form.style.display === "none" || form.style.display === "") {
        form.style.display = "block";
        saveButton.style.display = "inline-block";
      } else {
        form.style.display = "none";
        saveButton.style.display = "none";
      }

      const checkboxes = form.querySelectorAll('input[type="checkbox"]');
      checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", function () {
          updateCheckboxStates(checkboxes);
        });
      });
      updateCheckboxStates(checkboxes);
    });
  });

  saveButtons.forEach((saveButton) => {
    saveButton.addEventListener("click", function () {
      const section = this.getAttribute("data-section");
      const form = document.getElementById(section + "-form");
      form.style.display = "none";
      this.style.display = "none";
    });
  });

  const updateCheckboxStates = (checkboxes) => {
    const selectedCount = Array.from(checkboxes).filter(
      (cb) => cb.checked
    ).length;
    checkboxes.forEach((checkbox) => {
      checkbox.disabled = selectedCount >= maxSelections && !checkbox.checked;
    });
  };
});
