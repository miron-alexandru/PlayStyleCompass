$(document).ready(function () {
    $("#resend-link").click(function (e) {
        e.preventDefault();

        let url = $(this).data("url");

        $.get(url, function (data) {
            if (data.success) {
                $("#success-message").html(data.message);
            } else {
                $("#success-message").html(data.error_message);
            }
        });

        setTimeout(function () {
            location.reload();
        }, 1500);
    });
});