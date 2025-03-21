from django.contrib import admin

from .models import (
    UserPreferences,
    Game,
    Review,
    SharedGame,
    Franchise,
    Character,
    GameModes,
    News,
    GameList,
    ListReview,
    GameStores,
    ListComment,
    Poll,
    PollOption,
    Vote,
    Deal,
)

admin.site.register(UserPreferences)
admin.site.register(Game)
admin.site.register(Review)
admin.site.register(SharedGame)
admin.site.register(Franchise)
admin.site.register(Character)
admin.site.register(GameModes)
admin.site.register(News)
admin.site.register(GameList)
admin.site.register(ListReview)
admin.site.register(GameStores)
admin.site.register(ListComment)
admin.site.register(Poll)
admin.site.register(PollOption)
admin.site.register(Vote)
admin.site.register(Deal)
