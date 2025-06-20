from django.shortcuts import redirect, render
from core import models
from core.forms import CustomLoginForm, LoginForm, UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_view(request):
    """View for handling login"""

    form = LoginForm()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                messages.success(request, "Login Successful")
                login(request, user)
                return redirect('dashboard')
            else:
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
            return redirect('login')
    else:
        form = UserRegisterForm()
        
    return render(request, 'accounts/sign-up.html', {'form': form})


@login_required(login_url='login')
def dashboard(request):
    """View for dashboard"""

    active_landlords_count = models.User.objects.filter(app_level_role='landlord', is_verify=True).count()
    inactive_landlord_count = models.User.objects.filter(app_level_role='landlord', is_verify=False).count()

    # active_tenants_count = models.User.objects

    return render(request, 'dashboard/dashboard.html', 
                  {
                      'active_landlords_count': active_landlords_count or 0,
                      'inactive_landlord_count': inactive_landlord_count or 0
                   })


def logout_view(request):
    """Logout view"""

    logout(request)
    messages.success(request, "Logout Successful")
    return redirect('login')


def properties(request):
    """Properties view"""

    if request.user.is_authenticated:
        if request.user.app_level_role == 'landlord':
            properties = models.Property.objects.filter(landlord=request.user)
        else:
            properties = models.Property.objects.all()

    return render(request, 'dashboard/properties.html', {'properties': properties})

