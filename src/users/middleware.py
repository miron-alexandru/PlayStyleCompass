from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation


class UserTimezoneMiddleware:
    """Middleware to update the user's timezone based on the detected timezone
    stored in the session."""

    def __init__(self, get_response):
        self.get_response = get_response
        return

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            if request.session.get("detected_tz"):
                tz = timezone.get_current_timezone()
                if tz:
                    tz = str(tz)
                    try:
                        if tz != request.user.userprofile.timezone:
                            request.user.userprofile.timezone = tz
                            request.user.userprofile.save()
                    except ObjectDoesNotExist:
                        pass

        return response


class UserLanguageMiddleware:
    """Middleware used to set the language preference for users based on their user profile."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            language = getattr(request.user.userprofile, "language", "en")
            translation.activate(language)
            request.session["django_language"] = language
        response = self.get_response(request)
        return response
