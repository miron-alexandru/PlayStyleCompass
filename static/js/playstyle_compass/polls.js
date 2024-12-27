document.addEventListener("DOMContentLoaded", function() {
  window.toggleResults = function(pollId) {
    const resultsDiv = document.getElementById('results-' + pollId);
    if (resultsDiv.style.display === 'none') {
      resultsDiv.style.display = 'block';
    } else {
      resultsDiv.style.display = 'none';
    }
  }

  function confirmDelete() {
    return confirm("{% trans 'Are you sure you want to delete this poll?' %}");
  }

  document.querySelectorAll('.poll-card form').forEach(form => {
    const voteButton = form.querySelector('.vote-button');
    if (voteButton) { 
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
