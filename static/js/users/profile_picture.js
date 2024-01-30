document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.querySelector("#id_profile_picture");
  const uploadButton = document.querySelector("#uploadButton");

  fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
      uploadButton.removeAttribute("disabled");
    } else {
      uploadButton.setAttribute("disabled", "disabled");
    }
  });
});
