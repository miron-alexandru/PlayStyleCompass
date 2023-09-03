from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomRegistrationForm, DeleteAccountForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required



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
