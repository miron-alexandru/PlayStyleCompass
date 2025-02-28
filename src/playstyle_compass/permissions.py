from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from users.models import UserProfile


class HasValidAPIKey(BasePermission):
    def has_permission(self, request, view):
        api_key = request.GET.get("api_key")

        if not api_key:
            api_key = request.headers.get("Authorization")

        if not api_key:
            raise AuthenticationFailed(
                "API key missing from both query parameters and header"
            )

        try:
            user_profile = UserProfile.objects.get(api_key=api_key)
        except UserProfile.DoesNotExist:
            raise AuthenticationFailed("Invalid API key")

        return True
