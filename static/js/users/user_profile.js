document.addEventListener("DOMContentLoaded", function () {
  let toggleStat = document.querySelectorAll(".toggle-stat");

  toggleStat.forEach(function (button) {
    button.addEventListener("click", function () {
      const statName = button.dataset.stat;
      let { userId } = button.dataset;

      fetch(toggleStatUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          statName: statName,
          userId: userId,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          let icon = button.querySelector("i");
          if (data.show) {
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");
          } else {
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
          }
          let statContent = button
            .closest(".stat-item")
            .querySelector(".stat-content");
          statContent.innerHTML = data.show
            ? `<a href="${translate(statUrls[statName])}">${translate(statDisplayText[statName])}</a>`
            : `<span>${translate(statDisplayText[statName])}</span>`;
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });
});


document.addEventListener("DOMContentLoaded", function() {
  const actionsContainer = document.getElementById('user-actions');
  const recipientId = Number(actionsContainer.dataset.user_id);
  const ws = new WebSocket(`ws://${window.location.host}/ws/online-status/${recipientId}/`);

  ws.onmessage = function(event) {
      const data = JSON.parse(event.data);
      const statusElement = document.getElementById('status');
      
      if (statusElement) {
          statusElement.innerText = data.status ? translate('Online') : translate('Offline');

          if (data.status) {
              statusElement.classList.remove('offline');
              statusElement.classList.add('online');
          } else {
              statusElement.classList.remove('online');
              statusElement.classList.add('offline');
          }
      }
  };
});