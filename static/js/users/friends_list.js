document.addEventListener("DOMContentLoaded", () => {
  const protocol = location.protocol === "https:" ? "wss" : "ws"
  new WebSocket(`${protocol}://${location.host}/ws/presence/`)

  const friends = document.querySelectorAll(".friend-card")

  friends.forEach(friend => {
    const recipientId = Number(
      friend.querySelector(".recipient-id").getAttribute("content")
    )

    const statusElement = friend.querySelector(".status")

    if (!recipientId || !statusElement) {
      return
    }

    fetch(`/users/status/${recipientId}/`)
      .then(r => r.json())
      .then(data => {
        statusElement.innerText = data.status
          ? translate("Online")
          : translate("Offline")

        if (data.status) {
          statusElement.classList.add("online")
          statusElement.classList.remove("offline")
        } else {
          statusElement.classList.add("offline")
          statusElement.classList.remove("online")
        }
      })
      .catch(() => {
        statusElement.innerText = translate("Offline")
        statusElement.classList.add("offline")
        statusElement.classList.remove("online")
      })
  })
})

function onRemoveFriend() {
  location.reload()
}

function triggerRemoveFriend(friend_id) {
  removeFriend(friend_id, onRemoveFriend)
}
