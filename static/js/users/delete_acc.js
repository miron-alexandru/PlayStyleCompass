document.addEventListener("DOMContentLoaded", function () {
    const deleteButton = document.getElementById("delete-button");
    const deleteForm = document.getElementById("delete-form");

    deleteButton.addEventListener("click", function () {
        if (confirm("Confirm")) {
            deleteForm.submit();
        }
    });
});
