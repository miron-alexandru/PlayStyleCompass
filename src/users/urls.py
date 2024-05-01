"""Defines URL patterns."""

from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.custom_logout, name="logout"),
    path("register/", views.register, name="register"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="account_actions/password_reset_form.html",
            subject_template_name="account_actions/password_reset_subject.txt",
            html_email_template_name="account_actions/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path("change_password/", views.change_password, name="change_password"),
    path("change_email/", views.change_email, name="change_email"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path("profile_picture/", views.update_profile_picture, name="profile_picture"),
    path(
        "change-profile-name/",
        views.ProfileUpdateView.as_view(),
        name="change_profile_name",
    ),
    path(
        "password_change-done/", views.change_password_done, name="change_password_done"
    ),
    path("change_email/done/", views.change_email_done, name="change_email_done"),
    path(
        "change_email/success", views.change_email_success, name="change_email_success"
    ),
    path("contact/", views.contact, name="contact"),
    path("contact_success/", views.contact_success, name="contact_success"),
    path(
        "resend-activation-link/",
        views.resend_activation_link,
        name="resend_activation_link",
    ),
    path(
        "confirm_email_change/<str:uidb64>/<str:token>/",
        views.confirm_email_change,
        name="confirm_email_change",
    ),
    path("friends/<user_id>", views.friends_list_view, name="friends_list"),
    path("friend_remove ", views.remove_friend, name="remove_friend"),
    path(
        "send_friend_request/<int:user_id>/",
        views.send_friend_request,
        name="friend_request",
    ),
    path(
        "friend_request_cancel/",
        views.cancel_friend_request,
        name="friend_request_cancel",
    ),
    path(
        "friend_requests/<user_id>/", views.friend_requests_view, name="friend_requests"
    ),
    path(
        "friend_request_accept/<friend_request_id>/",
        views.accept_friend_request,
        name="friend_request_accept",
    ),
    path(
        "friend_request_decline/<friend_request_id>/",
        views.decline_friend_request,
        name="friend_request_decline",
    ),
    path("view_profile/<str:profile_name>/", views.view_profile, name="view_profile"),
    path("toggle_show_stats/", views.toggle_show_stat, name="toggle_show_stat"),
    path("send_message/<int:user_id>", views.send_message, name="send_message"),
    path("inbox/", views.inbox, name="inbox"),
    path("delete_messages/", views.delete_messages, name="delete_messages"),
    path(
        "mark_notification_as_read/<int:notification_id>/",
        views.mark_notification_as_read,
        name="mark_notification_as_read",
    ),
    path(
        "mark_notification_as_read/",
        views.mark_notification_as_read,
        name="mark_notification_as_read",
    ),
    path(
        "delete_notification/<int:notification_id>/",
        views.delete_notification,
        name="delete_notification",
    ),
    path(
        "delete_notification/",
        views.delete_notification,
        name="delete_notification",
    ),
    path(
        "check_authentication/", views.check_authentication, name="check_authentication"
    ),
    path("take_gaming_quiz/", views.quiz_view, name="gaming_quiz"),
    path(
        "quiz_recommendations/", views.quiz_recommendations, name="quiz_recommendations"
    ),
]
