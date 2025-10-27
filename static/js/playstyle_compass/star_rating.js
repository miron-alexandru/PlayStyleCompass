const starWidth = 20;

$.fn.stars = function () {
  return $(this).each(function () {
    const rating = Math.max(0, Math.min(5, parseFloat($(this).html())));
    $(this).html(
      $('<span class="filled" />').width(rating * starWidth)
    );
  });
};

$(document).ready(function () {
  $("span.stars").stars();
  $(".rating").each(function () {
    $(this).show();
  });
});