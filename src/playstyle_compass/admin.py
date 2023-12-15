from django.contrib import admin

from .models import UserPreferences, Game, Review

admin.site.register(UserPreferences)
admin.site.register(Game)
admin.site.register(Review)
