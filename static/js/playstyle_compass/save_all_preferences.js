$(document).ready(function() {
  $("#save-all-button").click(function(event) {
    event.preventDefault();
    var successfulSubmissions = 0;

    $("#history-section form, #genres-section form, #platforms-section form").each(function() {
      $.ajax({
        type: $(this).attr('method'),
        url: $(this).attr('action'),
        data: $(this).serialize(),
        success: function(response) {
          successfulSubmissions++;
          
        if (successfulSubmissions === $("#history-section form, #genres-section form, #platforms-section form").length) {
            location.reload();
          }
        },
      });
    });
  });
});