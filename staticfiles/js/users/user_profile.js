function onRemoveFriend() {
  location.reload();
}

function triggerRemoveFriend(friend_id) {
  removeFriend(friend_id, onRemoveFriend);
}

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


document.addEventListener('DOMContentLoaded', function() {
    const blockToggleButton = document.getElementById('block-toggle-button');
    const blockUrl = blockToggleButton.getAttribute('data-block-url');
    const unblockUrl = blockToggleButton.getAttribute('data-unblock-url');
    const checkUrl = blockToggleButton.getAttribute('data-check-url');

    function updateBlockButton() {
        fetch(checkUrl)
            .then(response => response.json())
            .then(data => {
                if (data.is_blocked) {
                    blockToggleButton.textContent = translate("Unblock");
                    blockToggleButton.classList.remove('block');
                    blockToggleButton.classList.add('unblock');
                    blockToggleButton.onclick = () => unblockUser();
                } else {
                    blockToggleButton.textContent = translate("Block");
                    blockToggleButton.classList.remove('unblock');
                    blockToggleButton.classList.add('block');
                    blockToggleButton.onclick = () => blockUser();
                }
            });
    }

    updateBlockButton();

    function blockUser() {
        fetch(blockUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            updateBlockButton();
        });
    }

    function unblockUser() {
        fetch(unblockUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            updateBlockButton();
        });
    }

});