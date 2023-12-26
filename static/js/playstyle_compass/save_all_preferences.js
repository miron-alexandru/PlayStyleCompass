$(document).ready(function () {
  $("#save-all-button").click(function (event) {
    event.preventDefault();
    let successfulSubmissions = 0;
    const totalForms = $("#history-section form, #genres-section form, #platforms-section form").length;

    // Show loading spinner
    $("#saving-spinner").show();

    $("#history-section form, #genres-section form, #platforms-section form").each(function () {
      const currentForm = $(this);

      $.ajax({
        type: currentForm.attr('method'),
        url: currentForm.attr('action'),
        data: currentForm.serialize(),
        success: function (response) {
          successfulSubmissions++;

          if (successfulSubmissions === totalForms) {
            setTimeout(function () {
              $("#saving-spinner").hide();
              location.reload();
            }, 1500);
          }
        },
      });
    });
  });
});
