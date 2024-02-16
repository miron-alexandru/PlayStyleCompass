document.querySelectorAll(".overview").forEach(function (truncatedText) {
  let fullText = truncatedText.parentNode.querySelector(".full-text");
  let readButton = truncatedText.parentNode.querySelector(".read-button");
  if (truncatedText.innerHTML === fullText.innerHTML) {
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
    button.innerHTML = translate("[Read more...]");
  } else {
    truncatedText.style.display = "none";
    fullText.style.display = "inline";
    button.innerHTML = translate("[Read less...]");
  }
}

function lazyLoadVideos() {
    const lazyVideos = document.querySelectorAll('.lazy-video');
    lazyVideos.forEach(video => {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const videoUrl = video.getAttribute('data-src');
                    video.innerHTML = `<iframe width="350" height="190" src="${videoUrl}" frameborder="0" allowfullscreen></iframe>`;
                    observer.unobserve(video);
                }
            });
        });
        observer.observe(video);
    });
}

document.addEventListener('DOMContentLoaded', lazyLoadVideos);
