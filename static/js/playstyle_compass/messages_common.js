$(document).ready(function () {
  $("#messages-received-btn").click(function () {
    $("#sent-messages").hide();
    $("#received-messages").show();

    $("#messages-received-btn").addClass("active");
    $("#messages-sent-btn").removeClass("active");
  });

  $("#messages-sent-btn").click(function () {
    $("#received-messages").hide();
    $("#sent-messages").show();

    $("#messages-sent-btn").addClass("active");
    $("#messages-received-btn").removeClass("active");
  });
});

document.addEventListener('DOMContentLoaded', function () {
  let selectAllButton = document.querySelector('.select-all-button');
  let deleteButton = document.querySelector('.delete-button');
  let messagesCheckboxes;

  function updateButtonText() {
    if (messagesCheckboxes.length === 0) {
      selectAllButton.textContent = 'Select All';
      deleteButton.disabled = true;
      return;
    }


    let allChecked = Array.from(messagesCheckboxes).every(function (checkbox) {
      return checkbox.checked;
    });

    selectAllButton.textContent = allChecked ? 'Unselect All' : 'Select All';

    deleteButton.disabled = !Array.from(messagesCheckboxes).some(function (checkbox) {
      return checkbox.checked;
    });
  }

  function updateCheckboxes(tabId) {
    let selector = (tabId === 'messages-received-btn') ? '.received-messages' : '.sent-messages';
    messagesCheckboxes = document.querySelectorAll(`${selector} .message-checkbox`);
  }

  selectAllButton.addEventListener('click', function () {
    let activeTab = document.querySelector('.category-button.active').id;
    updateCheckboxes(activeTab);

    messagesCheckboxes.forEach(function (checkbox) {
      checkbox.checked = !checkbox.checked;
    });

    updateButtonText();
  });

  let tabButtons = document.querySelectorAll('.category-button');
  tabButtons.forEach(function (tabButton) {
    tabButton.addEventListener('click', function () {
      updateCheckboxes(tabButton.id);
      updateButtonText();
    });
  });

  messagesCheckboxes = document.querySelectorAll('.message-checkbox');
  messagesCheckboxes.forEach(function (checkbox) {
    checkbox.addEventListener('click', updateButtonText);

  });
});