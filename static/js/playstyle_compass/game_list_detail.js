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
      location.reload();
    })
    .catch(error => {
      const errors = JSON.parse(error.message);
      alert("Error: " + Object.values(errors).join(", "));
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const editButton = document.querySelector('.edit-review-button');

  if (editButton) {
    editButton.addEventListener('click', function () {
      const reviewId = this.getAttribute('data-id');
      const existingReviewDiv = this.closest('.existing-review');
      if (!existingReviewDiv) return;

      const title = existingReviewDiv.querySelector('.review-title').innerText;
      const rating = existingReviewDiv.querySelector('.review-rating').innerText;
      const reviewText = existingReviewDiv.querySelector('.review-text').innerText;
      const formActionUrl = this.getAttribute('data-action-url');

      existingReviewDiv.innerHTML = `
        <p class="reviews-head">${translate("Edit Your Review:")}</p>
        <form class="edit-review-form" action="${formActionUrl}" method="post">
          <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}" />
          <label for="id_title">${translate("Title")}</label>
          <input type="text" name="title" value="${title}" required />
          <label for="id_rating">${translate("Rating")}</label>
          <select name="rating">
            <option value="1" ${rating == 1 ? 'selected' : ''}>1</option>
            <option value="2" ${rating == 2 ? 'selected' : ''}>2</option>
            <option value="3" ${rating == 3 ? 'selected' : ''}>3</option>
            <option value="4" ${rating == 4 ? 'selected' : ''}>4</option>
            <option value="5" ${rating == 5 ? 'selected' : ''}>5</option>
          </select>
          <label for="id_review_text">${translate("Review")}</label>
          <textarea name="review_text" required>${reviewText}</textarea>
          <button type="submit" class="edit-review-button">${translate("Update Review")}</button>
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
            alert(data.message)
            location.reload();
          } else {
            console.error(data.errors);
          }
        })
        .catch(error => console.error('Error:', error));
      });
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const deleteButton = document.querySelector('.delete-review-button');

  if (deleteButton) {
    deleteButton.addEventListener('click', function () {
      const reviewId = this.getAttribute('data-id');
      const actionUrl = this.getAttribute('data-action-url');
      
      if (confirm('Are you sure you want to delete this review?')) {
        fetch(actionUrl, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
          },
        })
        .then(response => response.json())
        .then(data => {
          if (data.message) {
            alert(data.message);
            location.reload();
          } else if (data.errors) {
            alert('Failed to delete review.');
          }
        })
        .catch(error => console.error('Error:', error));
      }
    });
  }
});
