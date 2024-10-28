document.getElementById("like-button").addEventListener("click", function () {
  const url = this.getAttribute("data-url");
  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
    },
  })
  .then(response => response.json())
  .then(data => {
    const icon = document.querySelector("#like-button i");
    icon.className = data.liked ? "fa-solid fa-heart" : "fa-regular fa-heart";
    document.getElementById("like-count").textContent = data.like_count;
  });
});


const reviewForm = document.getElementById("review-form");

if (reviewForm) {
  reviewForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const url = this.action;

    fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": csrfToken,
      },
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(errorData => {
          throw new Error(JSON.stringify(errorData.errors));
        });
      }
      return response.json();
    })
    .then(data => {
      alert(data.message);
      const reviewsContainer = document.getElementById("reviews-container");

      const newReview = document.createElement("div");
      newReview.classList.add("review");
      newReview.innerHTML = `
        <p><strong>Title:</strong>${data.title}</p>
        <p><strong>Author:</strong>${data.author}</p>
        <p><strong>Rating:</strong> ${data.rating}</p>
        <p><strong>Review:</strong>${data.review_text}</p>
      `;

      reviewsContainer.prepend(newReview);
    })
    .catch(error => {
      const errors = JSON.parse(error.message);
      alert("Error: " + Object.values(errors).join(", "));
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const editButtons = document.querySelectorAll('.edit-review-button');

  function handleEditButtonClick(editButton) {
    const reviewId = editButton.getAttribute('data-id');
    const existingReviewDiv = editButton.closest('.existing-review');
    console.log(!existingReviewDiv);
    if (!existingReviewDiv) return;

    const title = existingReviewDiv.querySelector('.review-title').innerText;
    const rating = existingReviewDiv.querySelector('.review-rating').innerText;
    const reviewText = existingReviewDiv.querySelector('.review-text').innerText;
    const formActionUrl = editButton.getAttribute('data-action-url');

    existingReviewDiv.innerHTML = `
      <p class="reviews-head">Edit Your Review:</p>
      <form class="edit-review-form" action="${formActionUrl}" method="post">
        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}" />
        <label for="id_title">Title</label>
        <input type="text" name="title" value="${title}" required />
        <label for="id_rating">Rating</label>
        <select name="rating">
          <option value="1" ${rating == 1 ? 'selected' : ''}>1</option>
          <option value="2" ${rating == 2 ? 'selected' : ''}>2</option>
          <option value="3" ${rating == 3 ? 'selected' : ''}>3</option>
          <option value="4" ${rating == 4 ? 'selected' : ''}>4</option>
          <option value="5" ${rating == 5 ? 'selected' : ''}>5</option>
        </select>
        <label for="id_review_text">Review</label>
        <textarea name="review_text" required>${reviewText}</textarea>
        <button type="submit" class="edit-review-button">Update Review</button>
      </form>
    `;

    const editForm = existingReviewDiv.querySelector('.edit-review-form');
    editForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(editForm);

      fetch(editForm.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken,
        },
      })
      .then(response => {
        if (!response.ok) {
          return response.json().then(errorData => {
            throw new Error(JSON.stringify(errorData));
          });
        }
        return response.json();
      })
      .then(data => {
        if (data.message) {
          const reviewToUpdate = document.querySelector(`#reviews-container .review[data-id="${reviewId}"]`);

          if (reviewToUpdate) {
            reviewToUpdate.innerHTML = `
              <p><strong>Title: </strong>${data.title}</p>
              <p><strong>Author: </strong>${data.author}</p>
              <p><strong>Rating: </strong> ${data.rating}</p>
              <p><strong>Review: </strong>${data.review_text}</p>
            `;
          }

          const updatedReviewDiv = this.closest('.existing-review');
          updatedReviewDiv.innerHTML = `
            <p class="review-head">Your Review:<p>
            <p><strong>Title:</strong> <span class="review-title">${data.title}</span></p>
            <p><strong>Rating:</strong> <span class="review-rating">${data.rating}</span></p>
            <p><strong>Review:</strong> <span class="review-text">${data.review_text}</span></p>
          `;

          const newEditButton = document.createElement('button');
          newEditButton.className = 'edit-review-button';
          newEditButton.setAttribute('data-id', reviewId);
          newEditButton.setAttribute('data-action-url', formActionUrl);
          newEditButton.textContent = 'Edit Review';

          updatedReviewDiv.appendChild(newEditButton);

          newEditButton.addEventListener('click', function () {
            handleEditButtonClick(newEditButton);
          });
        } else {
          console.error(data.errors);
        }
      })
      .catch(error => console.error('Error:', error));
    });
  }

  editButtons.forEach(editButton => {
    editButton.addEventListener('click', function () {
      handleEditButtonClick(editButton);
    });
  });
});
