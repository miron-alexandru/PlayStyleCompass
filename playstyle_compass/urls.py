"""Defines URL patterns."""

from django.urls import path

from . import views

app_name = 'playstyle_compass'
urlpatterns = [
    path('', views.index, name='index'),
    path('gaming_preferences/', views.gaming_preferences, name='gaming_preferences'),
    path('preferences', views.update_preferences, name='update_preferences'),
]
