from django.contrib import admin

from .models import UserPreferences, Game, Review, SharedGame

admin.site.register(UserPreferences)
admin.site.register(Game)
admin.site.register(Review)
admin.site.register(SharedGame)
