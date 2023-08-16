from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import GamingPreferences, UserPreferences
from .forms import GamingPreferencesForm

def index(request):
    """Home Page"""
    return render(request, 'playstyle_compass/index.html')

@login_required
def gaming_preferences(request):
    """Add gaming preferences"""
    preferences = GamingPreferences.objects.filter(owner=request.user).order_by('date_added')
    context = {'gaming_preferences': preferences}
    return render(request, 'playstyle_compass/gaming_preferences.html', context)

@login_required
def update_preferences(request):
    """Update user preferences."""
    user = request.user

    try:
        user_preferences = UserPreferences.objects.get(user=user)
    except UserPreferences.DoesNotExist:
        user_preferences = None

    if request.method == 'POST':
        # Process the form submission and update the user's preferences
        gaming_history = request.POST.get('gaming_history')
        favorite_genres = request.POST.getlist('favorite_genres')
        platforms = request.POST.getlist('platforms')

        # Update the user's preferences in the database
        user_preferences, created = UserPreferences.objects.get_or_create(user=user)
        user_preferences.gaming_history = gaming_history
        user_preferences.favorite_genres = ', '.join(favorite_genres)
        user_preferences.platforms = ', '.join(platforms)
        user_preferences.save()

    context = {
        'user_preferences': user_preferences,
    }

    return render(request, 'playstyle_compass/update_preferences.html', context)


