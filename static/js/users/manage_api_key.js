document.addEventListener("DOMContentLoaded", function() {
  const keyManagement = document.getElementById("api-management");
  const generateKeyURL = keyManagement.dataset.generateKey;
  const revokeKeyURL = keyManagement.dataset.revokeKey;

  function copyToClipboard(elementId) {
    let textarea = document.getElementById(elementId);
    textarea.select();
    document.execCommand("copy");
    alert(translate("API Key copied to clipboard!"));
  }

  function generateApiKey() {
    fetch(generateKeyURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.api_key) {
        document.querySelector(".key-section").innerHTML = `
          <p class="key-title">${translate("Your API Key is...")}</p>
          <textarea id="api-key" readonly rows="2" cols="60">${data.api_key}</textarea>
          <button id="copy-key-button">${translate("Copy")}</button>
          <button id="revoke-key-button">${translate("Revoke API Key")}</button>
          <p id="key-status">${translate("API key successfully generated")}</p>
        `;
      } else {
        document.getElementById("key-status").textContent = translate("Failed to generate API key.");
      }
    })
    .catch(error => {
      console.error("Error generating API key:", error);
      document.getElementById("key-status").textContent = translate("An error occurred while generating the API key.");
    });
  }

  function revokeApiKey() {
    fetch(revokeKeyURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        document.querySelector(".key-section").innerHTML = `
          <p>${translate("Your API key has been revoked.")}</p>
          <button id="generate-key-button">${translate("Generate New API Key")}</button>
        `;
      } else {
        document.getElementById("key-status").textContent = translate("Failed to revoke API key.");
      }
    })
    .catch(error => {
      console.error("Error revoking API key:", error);
      document.getElementById("key-status").textContent = translate("An error occurred while revoking the API key.");
    });
  }

  document.addEventListener("click", function(event) {
    if (event.target.id === "copy-key-button") {
      copyToClipboard("api-key");
    }
    if (event.target.id === "generate-key-button") {
      generateApiKey();
    }
    if (event.target.id === "revoke-key-button") {
      revokeApiKey();
    }
  });
});
