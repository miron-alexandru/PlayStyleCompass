from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework_api_key.models import APIKey
from django.utils.translation import gettext as _
from .models import UserProfile


@login_required
def manage_api_key(request):
    """View to display the API key of the logged-in user."""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    api_key = profile.api_key if profile.api_key else None

    if request.method == "POST":
        return JsonResponse({"error": "Modifications are not allowed"}, status=403)

    context = {
        "page_title": _("Playstyle Compass :: Manage API Key"),
        "api_key": api_key,
    }

    return render(request, "account_actions/manage_api_key.html", context)


@login_required
def generate_api_key(request):
    """View to generate a new API key for the logged-in user."""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if not profile.api_key:
        api_key_obj, key = APIKey.objects.create_key(name=user.username)
        profile.api_key = key
        profile.save()

    return JsonResponse({"api_key": profile.api_key})


@login_required
def revoke_api_key(request):
    """View to revoke the API key of the logged-in user."""
    if request.method == "POST":
        user = request.user
        api_key_obj = APIKey.objects.filter(name=user.username, revoked=False).first()
        if api_key_obj:
            api_key_obj.revoked = True
            api_key_obj.save()

            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.api_key = None
            profile.save()

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"error": "No active API key found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)
