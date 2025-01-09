document.addEventListener('DOMContentLoaded', function() {
    const shareButton = document.querySelector('.btn-submit');
    const checkboxes = document.querySelectorAll('input[name="shared_with"]');
    
    function toggleShareButton() {
      const isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
      shareButton.disabled = !isChecked;
    }

    checkboxes.forEach(checkbox => {
      checkbox.addEventListener('change', toggleShareButton);
    });

    toggleShareButton();
  });