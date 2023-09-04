from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomRegistrationForm, DeleteAccountForm, EmailChangeForm, CustomPasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages 



def register(request):
    """View function for user registration."""
    if request.method != 'POST':
        form = CustomRegistrationForm()
    else:
        form = CustomRegistrationForm(data=request.POST)
        
        if form.is_valid():
            # Check if a user with the provided email already exists
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'This email address is already in use.')
            else:
                new_user = form.save()
                # Log the user in and then redirect to the home page.
                login(request, new_user)
                return redirect('playstyle_compass:index')

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
                return redirect('users:login')
            else:
                form.add_error('password', 'Incorrect password. Please try again.')

    else:
        form = DeleteAccountForm()

    context = {
        'form': form,
        'page_title': 'Delete Account :: PlayStyle Compass'
    }

    return render(request, 'registration/delete_account.html', context)

@login_required
def change_email(request):
    """View for changing a user's email address."""
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, user=request.user)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            request.user.email = new_email
            request.user.save()
            
            messages.success(request, 'Your email has been updated successfully.')
            return redirect('playstyle_compass:index')
    else:
        form = EmailChangeForm(user=request.user, initial={'current_email': request.user.email})

    context = {
        'form': form,
        'page_title': 'Change Email :: PlayStyle Compass'
    }

    return render(request, 'registration/change_email.html', context)

@login_required
def password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['new_password1']
            password2 = form.cleaned_data['new_password2']

            if password1 == password2:
                if not request.user.check_password(password1):
                    request.user.set_password(password1)
                    request.user.save()
                    messages.success(request, 'Your password has been changed successfully.')
                    return redirect('playstyle_compass:index')
                else:
                    messages.error(request, 'New password must be different from the old password.')
            else:
                form.add_error('new_password2', 'New passwords must match.')
        else:
            messages.error(request, 'There was an error in your submission. Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    context = {
        'form': form,
        'page_title': 'Change Password :: PlayStyle Compass'
    }

    return render(request, 'registration/password_change_form.html', context)