const translate = (key) => {
      const translations = {
        'ro': {
          'Favorites': 'Favorite',
          'In Queue': 'Programate',
          'Reviews': 'Recenzii'
        },
      };

      const pathSegments = window.location.pathname.split('/');
      const languageCode = pathSegments[1] || 'ro';

      return translations[languageCode]?.[key] || key;
    };

document.addEventListener("DOMContentLoaded", function () {
    let toggleStat = document.querySelectorAll(".toggle-stat");

    toggleStat.forEach(function (button) {
        button.addEventListener("click", function () {
            const statName = button.dataset.stat;
            let {userId} = button.dataset;

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

                    let statContent = button.closest('.stat-item').querySelector('.stat-content');
                    statContent.innerHTML = data.show ? `<a href="${translate(statUrls[statName])}">${translate(statDisplayText[statName])}</a>` : `<span>${translate(statDisplayText[statName])}</span>`;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });
});