NOTIFICATION_TEMPLATES_RO = {
    "message": (
        '<a class="notification-profile" title="Vizualizați profilul utilizatorului" href="{profile_url}">{user_in_notification}</a> '
        "ți-a trimis un mesaj!<br>"
        '<a class="notification-link" title="Navighează" href="{navigation_url}">Vezi inbox-ul</a>'
    ),
    "friend_request": (
        '<a class="notification-profile" title="Vizualizați profilul utilizatorului" href="{profile_url}">{user_in_notification}</a> '
        "ți-a trimis o cerere de prietenie!<br>"
        '<a class="notification-link" title="Navighează" href="{navigation_url}">Vezi cererile de prietenie</a>'
    ),
    "friend_request_accepted": (
        '<a class="notification-profile" title="Vizualizați profilul utilizatorului" href="{profile_url}">{user_in_notification}</a> '
        "ți-a acceptat cererea de prietenie!"
    ),
    "friend_request_declined": (
        '<a class="notification-profile" title="Vizualizați profilul utilizatorului" href="{profile_url}">{user_in_notification}</a> '
        "ți-a refuzat cererea de prietenie!"
    ),
    "follow": (
        '<a class="notification-profile" title="Vizualizați profilul utilizatorului" href="{profile_url}">{follower_profile_name}</a> '
        "a început să te urmărească!"
    ),
    "review": (
        '<a class="notification-profile" title="Vizualizați profilul" href="{profile_url}">{profile_name}</a> '
        'a postat o recenzie nouă pentru <a class="notification-link" title="Vizualizați jocul" href="{game_url}">{game_title}</a>!'
    ),
    "shared_game": (
        '<a class="notification-profile" title="Vizualizați profilul utilizatorului" href="{profile_url}">{user_in_notification}</a> '
        "tocmai ți-a distribuit un joc!<br>"
        '<a class="notification-link" title="Navigați" href="{navigation_url}">Navighează la jocurile distribuite</a>'
    ),
    "shared_game_list": (
        '<a class="notification-profile" href="{profile_url}">{profile_name}</a> ți-a distribuit o listă de jocuri '
        '<a href="{game_list_url}">{game_list_title}</a>'
    ),
    "shared_poll": (
        '<a class="notification-profile" href="{profile_url}">{profile_name}</a> ți-a distribuit un sondaj '
        '<a href="{poll_url}">{poll_title}</a>'
    ),
    "chat_message": (
        '<a class="notification-profile" title="Vizualizați profilul utilizatorului" href="{profile_url}">{user_in_notification}</a> '
        "ți-a trimis un mesaj nou în Chat!<br>"
        '<a class="notification-link" title="Deschide Chatul" href="{navigation_url}">Deschide Chatul</a>'
    ),
}
