document.addEventListener('DOMContentLoaded', function () {
  const receivedBtn = document.getElementById('messages-received-btn');
  const sentBtn = document.getElementById('messages-sent-btn');
  
  const isPageRefresh = performance.navigation.type === 1;

  if (!isPageRefresh) {
    sessionStorage.removeItem('activeCategory');
  }

  const storedCategory = sessionStorage.getItem('activeCategory') || 'received';

  if (storedCategory === 'received') {
    toggleMessages("#received-messages", "#sent-messages");
    toggleActiveClass(receivedBtn, sentBtn);
  } else {
    toggleMessages("#sent-messages", "#received-messages");
    toggleActiveClass(sentBtn, receivedBtn);
  }

  receivedBtn.addEventListener('click', function () {
    toggleMessages("#received-messages", "#sent-messages");
    toggleActiveClass(receivedBtn, sentBtn);

    sessionStorage.setItem('activeCategory', 'received');
  });

  sentBtn.addEventListener('click', function () {
    toggleMessages("#sent-messages", "#received-messages");
    toggleActiveClass(sentBtn, receivedBtn);

    sessionStorage.setItem('activeCategory', 'sent');
  });
});

function toggleMessages(showContainer, hideContainer) {
  $(hideContainer).hide();
  $(showContainer).show();
}

function toggleActiveClass(activateBtn, deactivateBtn) {
  $(activateBtn).addClass("active");
  $(deactivateBtn).removeClass("active");
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