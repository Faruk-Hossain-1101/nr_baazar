from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        # Get username and password from the submitted form
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in if authentication was successful
            login(request, user)
            return redirect('home')  # Replace 'home' with the URL name you want to redirect to after login
        else:
            # Add an error message for invalid credentials
            messages.error(request, 'Invalid username or password.')
    
    # For GET request, or if authentication fails, render the login page.
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login_view')