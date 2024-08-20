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


document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("toggle-image").addEventListener("click", function(event) {
        event.preventDefault();

        const imageContainer = document.getElementById("image-container");
        const toggleLink = document.getElementById("toggle-image");
        
        if (imageContainer.style.display === "none" || imageContainer.style.display === "") {
            imageContainer.style.display = "inline-block";
            toggleLink.textContent = translate("Hide");
        } else {
            imageContainer.style.display = "none";
            toggleLink.textContent = translate("Show");
        }
    });
});