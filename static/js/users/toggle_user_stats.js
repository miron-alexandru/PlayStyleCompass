document.addEventListener("DOMContentLoaded", function () {
    let toggleStat = document.querySelectorAll(".toggle-stat");

    toggleStat.forEach(function (button) {
        button.addEventListener("click", function () {
            const statName = button.dataset.stat;
            let userId = button.dataset.userId;

            fetch(toggleStatUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'statName': statName,
                    'userId': userId
                }),
            })
            .then(response => response.json())
            .then(data => {

                let icon = button.querySelector('i');
                if (data.show) {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                } else {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                }

                var statContent = button.closest('.stat-item').querySelector('.stat-content');
                statContent.innerHTML = data.show ? `<a href="${statUrls[statName]}">${statDisplayText[statName]}</a>` : `<span>${statDisplayText[statName]}</span>`;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});