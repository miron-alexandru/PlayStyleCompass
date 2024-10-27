document.querySelectorAll(".overview").forEach(function (truncatedText) {
  let fullText = truncatedText.parentNode.querySelector(".full-text");
  let readButton = truncatedText.parentNode.querySelector(".read-button");
  if (truncatedText.textContent === fullText.textContent) {
    readButton.style.display = "none";
  } else {
    readButton.style.display = "inline";
  }
});

function readMore(button) {
  let parent = button.parentNode;
  let truncatedText = parent.querySelector(".overview");
  let fullText = parent.querySelector(".full-text");

  if (truncatedText.style.display === "none") {
    truncatedText.style.display = "inline";
    fullText.style.display = "none";
    button.textContent = translate("[Read more...]");
  } else {
    truncatedText.style.display = "none";
    fullText.style.display = "inline";
    button.textContent = translate("[Read less...]");
  }
}

function toggleRequirements(button) {
  let parent = button.parentNode;
  let requirementsDiv = parent.nextElementSibling;

  if (
    requirementsDiv &&
    requirementsDiv.classList.contains("game-requirements")
  ) {
    if (button.textContent.trim() === translate("Show")) {
      requirementsDiv.style.display = "block";
      button.textContent = translate("Hide");
    } else {
      requirementsDiv.style.display = "none";
      button.textContent = translate("Show");
    }
  }
}

function toggleVideos(button) {
  let parent = button.parentNode;
  let videosDiv = parent.nextElementSibling;

  if (videosDiv && videosDiv.classList.contains("gameplay-videos")) {
    if (button.textContent.trim() === translate("Show")) {
      videosDiv.style.display = "flex";
      button.textContent = translate("Hide");
    } else {
      videosDiv.style.display = "none";
      button.textContent = translate("Show");
    }
  }
}

function lazyLoadVideos() {
  const lazyVideos = document.querySelectorAll(".lazy-video");
  lazyVideos.forEach((video) => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const videoUrl = video.getAttribute("data-src");
          video.innerHTML = `<iframe width="350" height="190" src="${videoUrl}" frameborder="0" allowfullscreen></iframe>`;
          observer.unobserve(video);
        }
      });
    });
    observer.observe(video);
  });
}

document.addEventListener("DOMContentLoaded", lazyLoadVideos);
