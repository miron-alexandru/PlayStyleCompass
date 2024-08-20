const countdownDuration = 5;
const countdownElement = document.getElementById("countdown");
let seconds = countdownDuration;

const currentLanguage = window.location.pathname.split("/")[1];

const countdownInterval = setInterval(function () {
  seconds--;
  countdownElement.textContent = seconds + translate(" seconds");
  if (seconds <= 0) {
    clearInterval(countdownInterval);
    window.location.href = "/" + currentLanguage;
  }
}, 1000);
