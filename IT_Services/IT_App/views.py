from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UserRegistrationForm, OTPVerificationForm, ServiceForm
from .models import Service
from .forms import ServiceForm, SubscriptionForm
from decimal import Decimal
import random

# Generate OTP
def generate_otp():
    return random.randint(100000, 999999)

# User Registration View (Step 1)
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            otp = generate_otp()

            # Send OTP via email
            send_mail(
                'Your OTP for Registration',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            # Temporarily store user data and OTP in session
            request.session['user_data'] = {
                'username': form.cleaned_data.get('username'),
                'email': email,
                'password': form.cleaned_data.get('password'),
            }
            request.session['otp'] = otp

            # Redirect to OTP verification page
            return redirect('otp_verification')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

# OTP Verification View (Step 2)
def otp_verification(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            user_otp = form.cleaned_data.get('otp')
            session_otp = request.session.get('otp')

            if str(user_otp) == str(session_otp):  # Compare OTP
                user_data = request.session.get('user_data')

                # Create the user
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                )

                # Automatically log the user in
                login(request, user)

                messages.success(request, "Account created and logged in successfully!")
                return redirect('home')  # Redirect to the home page
            else:
                messages.error(request, "Invalid OTP. Please try again.")
    else:
        form = OTPVerificationForm()

    return render(request, 'otp_verification.html', {'form': form})

# Custom Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

# Home View (Protected)
@login_required
def home(request):
    services = Service.objects.filter(active=True)  # Only display active services
    return render(request, 'home.html', {'services': services})


# Subscription Page View
@login_required
def subscribe_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            # Calculate net price including GST
            messages.success(request, 'You have successfully subscribed to the service!')
            return redirect('home')
    else:
        form = SubscriptionForm()

    # Calculate net price with GST
    service_tax = Decimal(service.service_tax)
    service_price = Decimal(service.service_price)
    net_price = service_price + (service_price * service_tax / 100)

    return render(request, 'subscribe_service.html', {
        'service': service,
        'form': form,
        'net_price': net_price
    })


### CRUD Operations for the Service Model ###

# List all services
@login_required
def service_list(request):
    services = Service.objects.all()
    return render(request, 'service_list.html', {'services': services})

# Create a new service
@login_required
def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service created successfully!')
            return redirect('service_list')
    else:
        form = ServiceForm()
    return render(request, 'create_service.html', {'form': form})

# View single service
@login_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'service_detail.html', {'service': service})

# Update a service
@login_required
def update_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('service_detail', pk=pk)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'update_service.html', {'form': form, 'service': service})

# Delete a service
@login_required
def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('service_list')
    return render(request, 'delete_service.html', {'service': service})
