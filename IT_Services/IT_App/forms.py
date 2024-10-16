from django import forms
from django.contrib.auth.models import User
from .models import Service

# User Registration Form
class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
# OTP Verification Form
class OTPVerificationForm(forms.Form):
    otp = forms.IntegerField(required=True, label='Enter the OTP')

# Login Form
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


# Service Form for CRUD operations
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'service_name', 
            'payment_terms', 
            'service_price', 
            'service_package', 
            'service_tax', 
            'service_image',
            'active'
        ]

    # Optional: Customizing widgets for better UX
    service_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter service name', 'class': 'form-control'})
    )
    payment_terms = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter payment terms', 'class': 'form-control', 'rows': 3})
    )
    service_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'placeholder': 'Enter service price', 'class': 'form-control'})
    )
    service_package = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter service package', 'class': 'form-control'})
    )
    service_tax = forms.DecimalField(
        widget=forms.NumberInput(attrs={'placeholder': 'Enter service tax', 'class': 'form-control'})
    )
    service_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

class SubscriptionForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea, label='Delivery Address')