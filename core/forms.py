from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

from core.models import Property

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'role']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        if role == 'landlord':
            user.app_level_role = 'landlord'
        else:
            user.password = "Tenant@123"
            user.app_level_role = "tenant"
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class CustomLoginForm(AuthenticationForm):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        })
    )


class CreatePropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'address', 'description', 'image', 'number_of_units']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Property Name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Property Address'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Property Description'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'number_of_units': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Number of Unit'}),
        }