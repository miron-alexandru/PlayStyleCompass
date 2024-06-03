$(document).ready(function () {
  const saveAllButton = $("#save-all-button");

  saveAllButton.click(function (event) {
    event.preventDefault();
    
    const formData = $("#history-section form, #genres-section form, #themes-section form, #platforms-section form").serialize();

    $("#saving-spinner").show();

    $.ajax({
      type: "POST",
      url: saveAllButton.data("save-all-url"),
      data: formData,
      headers: {
        "X-CSRFToken": csrfToken,
      },
      success: function (response) {
        setTimeout(function () {
          $("#saving-spinner").hide();
          location.reload();
        }, 1000);
      },
    });
  });
});
