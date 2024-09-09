from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.i18n import set_language
from users import views
from django.conf.urls.i18n import i18n_patterns

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("playstyle_compass.urls")),
    path("users/", include("users.urls")),
    path("users/", include("social_django.urls", namespace="social")),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path(
        "confirm-deletion/<uidb64>/<token>/",
        views.confirm_deletion,
        name="confirm_deletion",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="account_actions/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="account_actions/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="account_actions/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
)

urlpatterns += [
    path("i18n/", include("django.conf.urls.i18n")),
    path("rosetta/", include("rosetta.urls")),
    path("tz_detect/", include("tz_detect.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
