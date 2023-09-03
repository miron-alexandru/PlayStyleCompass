from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('password-reset/',
        auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        subject_template_name='registration/password_reset_subject.txt',
        html_email_template_name='registration/password_reset_email.html',
        ),
    name='password_reset'),
    path('delete_account/', views.delete_account, name='delete_account'),
]