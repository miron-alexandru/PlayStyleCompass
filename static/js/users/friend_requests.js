function onFriendRequestAccepted() {
    location.reload();
  }

function onFriendRequestDeclined() {
    location.reload();
  }

function onCancelFriendRequest() {
    location.reload();
  }

function triggerAcceptFriendRequest(friend_request_id) {
    acceptFriendRequest(friend_request_id, onFriendRequestAccepted)
  }

function triggerDeclineFriendRequest(friend_request_id) {
    declineFriendRequest(friend_request_id, onFriendRequestDeclined)
  }

function triggerCancelFriendRequest(request_id) {
    cancelFriendRequest(request_id, onCancelFriendRequest)
  }