function confirmDelete(event) {
  const userConfirmed = confirm("Are you sure you want to delete this poll?");
  if (!userConfirmed) {
    event.preventDefault();
  }
}

document.addEventListener("DOMContentLoaded", function() {
  window.toggleResults = function(pollId) {
    const resultsDiv = document.getElementById('results-' + pollId);
    if (resultsDiv.style.display === 'none') {
      resultsDiv.style.display = 'block';
    } else {
      resultsDiv.style.display = 'none';
    }
  }

  document.querySelectorAll('.poll-card form[id^="delete-poll-form"]').forEach(form => {
    form.addEventListener('submit', confirmDelete);
  });

  document.querySelectorAll('.poll-card form').forEach(form => {
    const voteButton = form.querySelector('.vote-button');

    if (voteButton && !(voteButton.classList.contains('voted') || voteButton.classList.contains('closed'))) {
      const radioButtons = form.querySelectorAll('input[type="radio"]');

      function checkVoteStatus() {
        const isSelected = Array.from(radioButtons).some(radio => radio.checked);
        voteButton.disabled = !isSelected;
      }

      checkVoteStatus();

      radioButtons.forEach(radio => {
        radio.addEventListener('change', checkVoteStatus);
      });
    }
  });
});


document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".like-poll-button").forEach(button => {
    button.addEventListener("click", function () {
      const url = this.getAttribute("data-url");

      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then(response => response.json())
        .then(data => {
          const icon = this.querySelector("i");
          icon.className = data.liked ? "fa-solid fa-heart" : "fa-regular fa-heart";

          const likeCount = document.getElementById(`like-count-${data.poll_id}`);
          likeCount.textContent = data.like_count;
        });
    });
  });
});
