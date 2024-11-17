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


document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".like-review-button").forEach(button => {
    button.addEventListener("click", function () {
      const url = this.getAttribute("data-url");

      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then(response => response.json())
        .then(data => {
          const icon = this.querySelector("i");
          icon.className = data.liked ? "fa-solid fa-heart" : "fa-regular fa-heart";

          const likeCount = document.getElementById(`like-count-${data.review_id}`);
          likeCount.textContent = data.like_count;
        });
    });
  });
});


$(document).ready(function () {
  $(".game-list-review-stars").each(function () {
    const gameListReviewScore = parseInt($(this).data("review-score"), 10);
    const gameListReviewStarsHtml = generateGameListReviewStars(gameListReviewScore);
    $(this).html(gameListReviewStarsHtml);
  });
});

const generateGameListReviewStars = (score) => {
  let gameListReviewStarsHtml = "";
  for (let i = 1; i <= 5; i++) {
    gameListReviewStarsHtml += `<i class="fas fa-star ${
      i <= score ? "game-list-review-gold-star" : "game-list-review-empty-star"
    }"></i>`;
  }
  return gameListReviewStarsHtml;
};


document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.getElementById("toggle-comments-btn");
  const commentsDiv = document.getElementById("comments");

  toggleBtn.addEventListener("click", function () {
    const isHidden = commentsDiv.classList.contains("hidden");

    if (isHidden) {
      commentsDiv.classList.remove("hidden");
      toggleBtn.textContent = translate('Hide Comments');
    } else {
      commentsDiv.classList.add("hidden");
      toggleBtn.textContent = translate('Show Comments');
    }
  });
});


document.addEventListener('click', (event) => {
  if (event.target.classList.contains("delete-comment-btn")) {
    const deleteUrl = event.target.getAttribute("data-delete-url");
    const confirmed = confirm("Are you sure you want to delete this comment?");

    if (confirmed) {
      const commentElement = event.target.closest('.comment');
      
      fetch(deleteUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            commentElement.remove();
          } else {
            alert("Failed to delete the comment.");
          }
        })
        .catch(() => {
          alert("An error occurred. Please try again.");
        });
    }
  }
});


document.addEventListener('click', (event) => {
  if (event.target.classList.contains('edit-comment-btn')) {
    const editUrl = event.target.getAttribute('data-edit-url');

    fetch(editUrl, { method: 'GET' })
      .then(response => response.json())
      .then(data => {
        if (data.form) {
          const commentElement = event.target.closest('.comment');
          commentElement.innerHTML = data.form;

          const formWrapper = document.createElement('form');
          formWrapper.method = 'POST';
          formWrapper.action = editUrl;

          formWrapper.innerHTML = data.form;
          commentElement.innerHTML = '';
          commentElement.appendChild(formWrapper);

          const saveButton = document.createElement('button');
          saveButton.classList.add("save-edit-btn");
          saveButton.textContent = 'Save';
          saveButton.addEventListener('click', (e) => {
            e.preventDefault();
            const formData = new FormData(formWrapper);
            fetch(editUrl, {
              method: 'POST',
              body: formData,
              headers: {
                'X-CSRFToken': csrfToken,
              },
            })
              .then(response => response.json())
              .then(data => {
                if (data.message) {
                  alert(data.message);
                  location.reload();
                }
              });
          });

          formWrapper.appendChild(saveButton);
        }
      });
  }
});


document.addEventListener('DOMContentLoaded', function () {
  const commentForm = document.getElementById('comment-form');
  const commentSection = document.querySelector('.comment-section');
  const commentsSection = document.getElementById('comments');
  const postCommentUrl = commentSection.getAttribute('data-post-comment-url');
  
  commentForm.addEventListener('submit', function (e) {
    e.preventDefault();
    
    const formData = new FormData(commentForm);

    fetch(postCommentUrl, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest', 
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        const newComment = document.createElement('li');
        newComment.classList.add('comment');
        newComment.innerHTML = `
          <p class="comment-author-text">
            <a class="comment-author" href="${data.profile_url}">
              ${data.profile_name}
            </a> wrote:
          </p>
          <p class="list-comment">${data.comment_text}</p>
          <p class="comment-meta">Posted on ${data.created_at}</p>
          <button class="edit-comment-btn" data-edit-url="${data.edit_url}">
            Edit
          </button>
          <button class="delete-comment-btn" data-delete-url="${data.delete_url}">
            Delete
          </button>
        `;
        
        const commentList = commentsSection.querySelector('ul');
        if (commentList) {
          commentList.appendChild(newComment);
        } else {
          const newUl = document.createElement('ul');
          newUl.appendChild(newComment);
          commentsSection.appendChild(newUl);
        }

        const noCommentsMessage = document.getElementById('no-comments-msg');
        if (noCommentsMessage) {
          noCommentsMessage.style.display = 'none';
        }

        commentForm.reset();
      } else {
        alert("There was an error posting the comment.");
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert("There was an error posting the comment.");
    });
  });
});

