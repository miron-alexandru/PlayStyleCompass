from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('password-reset/',
        auth_views.PasswordResetView.as_view(
        template_name='account_actions/password_reset_form.html',
        subject_template_name='account_actions/password_reset_subject.txt',
        html_email_template_name='account_actions/password_reset_email.html',
        ),
    name='password_reset'),
    path('change_password/', views.change_password, name='change_password'),
    path('change_email/', views.change_email, name='change_email'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('profile/', views.update_profile, name='profile'),
    path('password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='account_actions/password_change_done.html'),
        name='password_change_done'
    ),
    path('change_email/done/', views.change_email_done, name='change_email_done'),

]