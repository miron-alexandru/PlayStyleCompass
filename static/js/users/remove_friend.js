function onRemoveFriend() {
  location.reload();
}

function triggerRemoveFriend(friend_id) {
  removeFriend(friend_id, onRemoveFriend)
}