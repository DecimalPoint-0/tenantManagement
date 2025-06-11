from django.shortcuts import redirect, render

from core.forms import UserRegisterForm


def login(request):
    """View for handling login"""

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

    return render(request, 'accounts/sign-in.html')

def register_view(request):
    """View for registration"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # login(request, user) 
            return redirect('login') 
    else:
        form = UserRegisterForm()
        
    return render(request, 'accounts/sign-up.html', {'form': form})