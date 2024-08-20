document.addEventListener("DOMContentLoaded", function () {
  const selectAllButton = document.querySelector(".select-all-button");
  const deleteButton = document.querySelector(".delete-button");
  let messagesCheckboxes;

  const updateButtonText = () => {
    if (!messagesCheckboxes || messagesCheckboxes.length === 0) {
      selectAllButton.textContent = translate("Select All");
      deleteButton.disabled = true;
      return;
    }

    const allChecked = Array.from(messagesCheckboxes).every(
      (checkbox) => checkbox.checked
    );

    selectAllButton.textContent = allChecked
      ? translate("Unselect All")
      : translate("Select All");

    deleteButton.disabled = !Array.from(messagesCheckboxes).some(
      (checkbox) => checkbox.checked
    );
  };

  const updateCheckboxes = () => {
    const checkboxContainer = document.querySelector(".messages-grid-inbox");
    messagesCheckboxes = checkboxContainer.querySelectorAll(".message-checkbox");
  };

  const toggleAllCheckboxes = () => {
    updateCheckboxes();

    const allChecked = Array.from(messagesCheckboxes).every(
      (checkbox) => checkbox.checked
    );

    messagesCheckboxes.forEach((checkbox) => (checkbox.checked = !allChecked));

    updateButtonText();
  };

  messagesCheckboxes = document.querySelectorAll(".message-checkbox");

  messagesCheckboxes.forEach((checkbox) =>
    checkbox.addEventListener("click", function() {
      console.log("Message selected:", checkbox.value);
      updateButtonText();
    })
  );

  selectAllButton.addEventListener("click", toggleAllCheckboxes);

  updateButtonText();
});
