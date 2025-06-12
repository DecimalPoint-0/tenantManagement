from django.shortcuts import redirect, render
from core import models
from core.forms import CustomLoginForm, LoginForm, UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import LoginView
from django.contrib import messages

def login_view(request):
    """View for handling login"""

    form = LoginForm()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                print("valid")
                messages.success(request, "Login Successful")
                login(request, user)
            else:
                print("not valid")
                messages.error(request, "Invalid Login Details")
        except ObjectDoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid email or password'})
    return render(request, 'accounts/sign-in.html', {'form': form})


def register_view(request):
    """View for registration"""

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login(request, user) 
            return redirect('login')
        else:
            print(form) 
    else:
        form = UserRegisterForm()
        
    return render(request, 'accounts/sign-up.html', {'form': form})