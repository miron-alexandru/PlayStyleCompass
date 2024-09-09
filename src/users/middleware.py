from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


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
