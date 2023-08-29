const countdownDuration = 5;
const countdownElement = document.getElementById("countdown");
let seconds = countdownDuration;

const countdownInterval = setInterval(function () {
  seconds--;
  countdownElement.textContent = seconds + " seconds";
  if (seconds <= 0) {
    clearInterval(countdownInterval);
    window.location.href = "/"; 
  }
}, 1000);