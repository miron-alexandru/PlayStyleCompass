document.addEventListener("DOMContentLoaded", function () {
  const deleteButtonDisabled = document.getElementById(
    "delete-button-disabled"
  );
  const deleteButton = document.getElementById("delete-button");
  const deleteForm = document.getElementById("delete-form");
  const passwordInput = document.getElementById("id_password");

  const confirmAndSubmit = function (event) {
    if (confirm("Are you sure you want to proceed?")) {
      deleteForm.submit();
    } else {
      event.preventDefault();
    }
  };

  if (deleteButton) {
    passwordInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        confirmAndSubmit();
      }
    });
    deleteButton.addEventListener("click", confirmAndSubmit);
  }

  if (passwordInput && deleteButtonDisabled) {
    passwordInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter" && !deleteButtonDisabled.disabled) {
        event.preventDefault();
      }
    });
  }
});
