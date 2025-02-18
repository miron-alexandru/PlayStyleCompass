from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from django.http import JsonResponse


@login_required
def access_token_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        refresh = RefreshToken(profile.api_refresh_token)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        profile.api_access_token = access_token
        profile.api_refresh_token = refresh_token
        profile.save()

        return JsonResponse({
            "access": access_token,
            "refresh": refresh_token
        })

    if not profile.api_access_token or not profile.api_refresh_token:
        refresh = RefreshToken.for_user(user)
        profile.api_access_token = str(refresh.access_token)
        profile.api_refresh_token = str(refresh)
        profile.save()

    token_data = {
        "access": profile.api_access_token,
        "refresh": profile.api_refresh_token,
    }

    return render(request, "account_actions/api_token.html", {"token_data": token_data})
