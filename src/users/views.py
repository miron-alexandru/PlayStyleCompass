from django.shortcuts import render, redirect
from django.contrib.auth import (
    login,
    logout,
    update_session_auth_hash,
    get_user_model,
)
from .forms import (
    CustomRegistrationForm,
    DeleteAccountForm,
    EmailChangeForm,
    CustomPasswordChangeForm,
    ProfilePictureForm,
    ContactForm,
    CustomAuthenticationForm,
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile
from .tokens import account_activation_token
from django.contrib.auth.views import LoginView

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.utils.encoding import (
    force_bytes,
    force_str,
)
from django.core.mail import EmailMessage
from django.utils.safestring import mark_safe
from django.http import JsonResponse



class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.userprofile.email_confirmed = True
        user.userprofile.save()
        user.save()

        messages.success(request, "Thank you for your email confirmation!")
        return redirect('playstyle_compass:index')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('playstyle_compass:index')

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("registration/activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        message = f'Hello <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on ' \
                  f'received activation link to confirm your registration. \
                  <b>Note:</b> If you cannot find the email in your inbox, we recommend checking your spam folder.'
        messages.success(request, mark_safe(message))
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')

def resend_activation_link(request):
    if request.method == 'GET':
        email = request.user.email
        user = User.objects.get(email=email)
        activateEmail(request, user, email)
    else:
        return JsonResponse({'success': False, 'error_message': 'Invalid request method'})

def register(request):
    """View function for user registration."""
    if request.method == 'POST':
        form = CustomRegistrationForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.save()

            user_profile = UserProfile(
                user=new_user,
                profile_name=form.cleaned_data['profile_name'],
            )

            user_profile.save()
            new_user.save()

            activateEmail(request, new_user, form.cleaned_data.get('email'))
            login(request, new_user)

            return redirect('playstyle_compass:index')

    else:
        form = CustomRegistrationForm()

    context = {
        'form': form,
        'page_title': 'Register :: PlayStyle Compass'
    }
    return render(request, 'registration/register.html', context)

@login_required
def delete_account(request):
    """View for deleting a user's account."""
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data['password']
            if request.user.check_password(password):
                request.user.delete()
                messages.success(request, "Your account has been successfully deleted!")
                return redirect('playstyle_compass:index')
            else:
                form.add_error('password', 'Incorrect password. Please try again.')

    else:
        form = DeleteAccountForm()

    context = {
        'form': form,
        'page_title': 'Delete Account :: PlayStyle Compass'
    }

    return render(request, 'account_actions/delete_account.html', context)

@login_required
def change_email(request):
    """View for changing a user's email address."""
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, user=request.user)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            request.user.email = new_email
            request.user.save()

            return redirect('users:change_email_done')
    else:
        form = EmailChangeForm(user=request.user, initial={'current_email': request.user.email})

    context = {
        'form': form,
        'page_title': 'Change Email :: PlayStyle Compass'
    }

    return render(request, 'account_actions/change_email.html', context)

@login_required
def change_email_done(request):
    messages.success(request, "Email Address Changed Successfully!")
    context = {
    'page_title': 'Email Change Done :: PlayStyle Compass',
    'response': 'You have changed your email address, go to the homepage by clicking the button below.'
    }
    return render(request, 'account_actions/change_succeeded.html', context)

@login_required
def change_password(request):
    """View for changing a user's password."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['new_password1']
            password2 = form.cleaned_data['new_password2']

            if password1 == password2:
                if not request.user.check_password(password1):
                    request.user.set_password(password1)
                    request.user.save()

                    update_session_auth_hash(request, request.user)
                    return redirect('users:change_password_done')
                else:
                    messages.error(request, 'New password must be different from the old password!')
            else:
                form.add_error('new_password2', 'New passwords must match.')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    context = {
        'form': form,
        'page_title': 'Change Password :: PlayStyle Compass',
    }

    return render(request, 'account_actions/password_change_form.html', context)

@login_required
def change_password_done(request):
    messages.success(request, "Password Changed Successfully!")
    context = {
    'page_title': 'Password Change Done :: PlayStyle Compass',
    'response': 'You have changed your password, go to te homepage by clicking the button below.'
    }
    return render(request, 'account_actions/change_succeeded.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.userprofile)

        if form.is_valid():
            form.save()
            return redirect('users:profile')

    else:
        form = ProfilePictureForm(instance=request.user.userprofile)

    context = {
        'form': form,
        'page_title': 'Change Profile Picture :: PlayStyle Compass'
    }

    return render(request, 'account_actions/update_profile.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            subject = 'New Conctat Us Submission'
            message = f'''
                Name: {contact_message.name}
                Email: {contact_message.email}
                Subject: {contact_message.subject}
                Message: {contact_message.message}
                Time: {contact_message.formatted_timestamp()}
            '''
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.EMAIL_USER_CONTACT]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            return redirect('users:contact_success')
    else:
        form = ContactForm()

    context = {
        'form': form,
        'page_title': 'Contact Us :: PlayStyle Compass'
    }

    return render(request, 'account_actions/contact.html', context)

@login_required
def contact_success(request):
    messages.success(request, 'Your message has been successfully submitted!')
    context = {
    'page_title': 'Contact Us Done :: PlayStyle Compass',
    'response': 'Thank you for contacting us! Our team will review it within 48 hours and get back to you as soon as possible. \
    Go to the homepage by clicking the button below.'
    }
    return render(request, 'account_actions/change_succeeded.html', context)