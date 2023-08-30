from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomRegistrationForm

def register(request):
    """View function for user registration."""
    if request.method != 'POST':
        # Display blank registration form.
        form = CustomRegistrationForm()
    else:
        # Process completed form.
        form = CustomRegistrationForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save()
            # Log the user in and then redirect to home page.
            login(request, new_user)
            return redirect('playstyle_compass:index')

    # Display a blank or invalid form.
    context = {
    'form': form,
    'page_title': 'Register :: PlayStyle Compass'}
    return render(request, 'registration/register.html', context)
