$(document).ready(function () {
  $("#received-games-btn").click(function () {
    $("#shared-games").hide();
    $("#received-games").show();

    $("#received-games-btn").addClass("active");
    $("#shared-games-btn").removeClass("active");
  });

  $("#shared-games-btn").click(function () {
    $("#received-games").hide();
    $("#shared-games").show();

    $("#shared-games-btn").addClass("active");
    $("#received-games-btn").removeClass("active");
  });
});

document.addEventListener('DOMContentLoaded', function () {
  let selectAllButton = document.querySelector('.select-all-button');
  let deleteButton = document.querySelector('.delete-button');
  let sharedGameCheckboxes;

  function updateButtonText() {
    if (sharedGameCheckboxes.length === 0) {
      selectAllButton.textContent = 'Select All';
      deleteButton.disabled = true;
      return;
    }


    let allChecked = Array.from(sharedGameCheckboxes).every(function (checkbox) {
      return checkbox.checked;
    });

    selectAllButton.textContent = allChecked ? 'Unselect All' : 'Select All';

    deleteButton.disabled = !Array.from(sharedGameCheckboxes).some(function (checkbox) {
      return checkbox.checked;
    });
  }

  function updateCheckboxes(tabId) {
    let selector = (tabId === 'received-games-btn') ? '.received-games' : '.shared-games';
    sharedGameCheckboxes = document.querySelectorAll(`${selector} .shared-game-checkbox`);
  }

  selectAllButton.addEventListener('click', function () {
    let activeTab = document.querySelector('.shared-games-button.active').id;
    updateCheckboxes(activeTab);

    sharedGameCheckboxes.forEach(function (checkbox) {
      checkbox.checked = !checkbox.checked;
    });

    updateButtonText();
  });

  let tabButtons = document.querySelectorAll('.shared-games-button');
  tabButtons.forEach(function (tabButton) {
    tabButton.addEventListener('click', function () {
      updateCheckboxes(tabButton.id);
      updateButtonText();
    });
  });

  sharedGameCheckboxes = document.querySelectorAll('.shared-game-checkbox');
  sharedGameCheckboxes.forEach(function (checkbox) {
    checkbox.addEventListener('click', updateButtonText);

  });
});