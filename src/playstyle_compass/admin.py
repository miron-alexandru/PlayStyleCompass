from django.contrib import admin

from .models import UserPreferences, Game, Review, SharedGame, Franchise

admin.site.register(UserPreferences)
admin.site.register(Game)
admin.site.register(Review)
admin.site.register(SharedGame)
admin.site.register(Franchise)
