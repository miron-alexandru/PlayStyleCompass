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
            </a> ${translate('wrote:')}
          </p>
          <p class="list-comment">${data.comment_text}</p>
          <p class="comment-meta">${translate('Posted on')} ${data.created_at}</p>
          <button class="edit-comment-btn" data-edit-url="${data.edit_url}">
            ${translate('Edit')}
          </button>
          <button class="delete-comment-btn" data-delete-url="${data.delete_url}">
            ${translate("Delete")}
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
        alert(translate("There was an error posting the comment."));
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert(translate("There was an error posting the comment."));
    });
  });
});


document.addEventListener('click', (event) => {
  if (event.target.classList.contains('edit-comment-btn')) {
    const editUrl = event.target.getAttribute('data-edit-url');

    fetch(editUrl, { method: 'GET' })
      .then(response => response.json())
      .then(data => {
        if (data.form) {
          const commentElement = event.target.closest('.comment');
          const originalContent = commentElement.innerHTML;

          commentElement.innerHTML = data.form;

          const saveButton = commentElement.querySelector('.save-edit-btn');
          if (saveButton) {
            saveButton.addEventListener('click', (e) => {
              e.preventDefault();

              const form = commentElement.querySelector('form');
              const textField = form.querySelector('textarea[name="text"]');
              const commentText = textField.value.trim();

              if (!commentText) {
                alert(translate("Comment text cannot be empty."));
                return;
              }

              const formData = new FormData(form);

              fetch(editUrl, {
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
                    commentElement.innerHTML = `
                      <p class="comment-author-text">
                        <a class="comment-author" href="${data.profile_url}">
                          ${data.profile_name}
                        </a> ${translate('wrote:')}
                      </p>
                      <p class="list-comment">${data.comment_text}</p>
                      <p class="comment-meta">Posted on ${data.created_at}</p>
                      <button class="edit-comment-btn" data-edit-url="${data.edit_url}">
                        ${translate("Edit")}
                      </button>
                      <button class="delete-comment-btn" data-delete-url="${data.delete_url}">
                        ${translate("Delete")}
                      </button>
                    `;
                    alert(translate("Comment updated successfully."));
                  } else {
                    alert(translate("There was an error updating the comment."));
                  }
                })
                .catch(error => {
                  console.error('Error:', error);
                  alert(translate("There was an error updating the comment."));
                });
            });
          }

          const cancelButton = commentElement.querySelector('.cancel-edit-btn');
          if (cancelButton) {
            cancelButton.addEventListener('click', (e) => {
              e.preventDefault();
              commentElement.innerHTML = originalContent;
            });
          }
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert(translate("There was an error loading the edit form."));
      });
  }
});


document.addEventListener('click', (event) => {
  if (event.target.classList.contains("delete-comment-btn")) {
    const deleteUrl = event.target.getAttribute("data-delete-url");
    const confirmed = confirm(translate("Are you sure you want to delete this comment?"));

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
            alert(translate("Failed to delete the comment."));
          }
        })
        .catch(() => {
          alert(translate("An error occurred. Please try again."));
        });
    }
  }
});