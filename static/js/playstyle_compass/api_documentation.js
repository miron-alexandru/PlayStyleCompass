document.addEventListener("DOMContentLoaded", function() {
const apiNavigation = document.querySelector(".api-navigation");
const scrollOffset = 155;

window.addEventListener("scroll", function () {
    if (window.scrollY >= scrollOffset) {
        apiNavigation.classList.add("fixed");
    } else {
        apiNavigation.classList.remove("fixed");
    }
});
});
