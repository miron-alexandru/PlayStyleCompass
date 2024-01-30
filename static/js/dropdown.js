$(document).ready(function () {
  $(".nav-item.dropdown").hover(
    function () {
      $(this).find(".dropdown-menu").stop(true, true).delay(200).fadeIn(300);
    },
    function () {
      $(this).find(".dropdown-menu").stop(true, true).delay(200).fadeOut(300);
    }
  );

  $(".nav-item.dropdown").on("click", function (e) {
    e.stopPropagation();
  });
});
