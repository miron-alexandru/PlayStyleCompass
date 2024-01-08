$(document).ready(function () {
  $("#messages-received-btn").click(function () {
    $("#sent-messages").hide();
    $("#received-messages").show();

    $("#messages-received-btn").addClass("active");
    $("#messages-sent-btn").removeClass("active");

    const sortOrder = $("#sort-order").val();
    sortMessages("#received-messages", sortOrder);
  });

  $("#messages-sent-btn").click(function () {
    $("#received-messages").hide();
    $("#sent-messages").show();

    $("#messages-sent-btn").addClass("active");
    $("#messages-received-btn").removeClass("active");

    const sortOrder = $("#sort-order").val();
    sortMessages("#sent-messages", sortOrder);
  });

  $("#sort-order").change(function () {
    const sortOrder = $("#sort-order").val();
    const activeTabId = $(".category-button.active").attr("id");
    const messagesContainerId = (activeTabId === "messages-received-btn") ? "#received-messages" : "#sent-messages";

    sortMessages(messagesContainerId, sortOrder);
  });
});


function sortMessages(containerId, sortOrder) {
  const messagesContainer = $(containerId);
  const messages = messagesContainer.find(".message-card").toArray();

  if (messages.length > 0) {
    messages.sort(function(a, b) {
      var timestampA = $(a).data("timestamp");
      var timestampB = $(b).data("timestamp");

      if (sortOrder === "asc") {
        return timestampA.localeCompare(timestampB);
      } else {
        return timestampB.localeCompare(timestampA);
      }
    });

    messagesContainer.empty().append(messages);
  } else {
    const emptyMessage = $("<p class='empty-category'></p>")
      .text(messagesContainer.data("empty-message") || "Empty.");
    messagesContainer.empty().append(emptyMessage);
  }
}



document.addEventListener('DOMContentLoaded', function () {
  const selectAllButton = document.querySelector('.select-all-button');
  const deleteButton = document.querySelector('.delete-button');
  let messagesCheckboxes;

  function updateButtonText() {
    if (messagesCheckboxes.length === 0) {
      selectAllButton.textContent = 'Select All';
      deleteButton.disabled = true;
      return;
    }

    const allChecked = Array.from(messagesCheckboxes).every(checkbox => checkbox.checked);

    selectAllButton.textContent = allChecked ? 'Unselect All' : 'Select All';
    deleteButton.disabled = !Array.from(messagesCheckboxes).some(checkbox => checkbox.checked);
  }

  function updateCheckboxes(tabId) {
    const selector = (tabId === 'messages-received-btn') ? '.received-messages' : '.sent-messages';
    messagesCheckboxes = document.querySelectorAll(`${selector} .message-checkbox`);
  }

  function toggleAllCheckboxes() {
    const activeTab = document.querySelector('.category-button.active').id;
    updateCheckboxes(activeTab);

    const allChecked = Array.from(messagesCheckboxes).every(checkbox => checkbox.checked);

    messagesCheckboxes.forEach(checkbox => checkbox.checked = !allChecked);

    updateButtonText();
  }

  let tabButtons = document.querySelectorAll('.category-button');
  tabButtons.forEach(tabButton => {
    tabButton.addEventListener('click', () => {
      updateCheckboxes(tabButton.id);
      updateButtonText();
    });
  });

  messagesCheckboxes = document.querySelectorAll('.message-checkbox');
  messagesCheckboxes.forEach(checkbox => checkbox.addEventListener('click', updateButtonText));

  selectAllButton.addEventListener('click', toggleAllCheckboxes);

  updateButtonText();
});