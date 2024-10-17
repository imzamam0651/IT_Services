from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
import random
from django.views.decorators.csrf import csrf_exempt
import razorpay

from .forms import UserRegistrationForm, OTPVerificationForm, LoginForm, ServiceForm, SubscriptionForm
from .models import Service, OTP


# Razorpay client setup
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Inactive until OTP is verified
            user.save()

            otp_code = random.randint(100000, 999999)
            OTP.objects.create(user=user, otp_code=otp_code)

            send_mail(
                'Your OTP Code',
                f'Your OTP is {otp_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            request.session['user_id'] = user.id
            return redirect('otp-verification')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# OTP Verification View
def otp_verification(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            otp_instance = OTP.objects.filter(user=user, otp_code=otp_code).first()
            if otp_instance:
                user.is_active = True
                user.save()
                otp_instance.delete()
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
    else:
        form = OTPVerificationForm()

    return render(request, 'otp_verification.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Logout View
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Home View (Requires Authentication)
@login_required
def home(request):
    services = Service.objects.filter(active=True)  # Show only active services
    return render(request, 'home.html', {'services': services})

### CRUD Operations for the Service Model ###

# List all services
@login_required
def service_list(request):
    services = Service.objects.all()
    return render(request, 'service_list.html', {'services': services})

# Create Service View (Admin/Authorized Users)
@login_required
def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service created successfully.')
            return redirect('home')
    else:
        form = ServiceForm()
    return render(request, 'create_service.html', {'form': form})

# Single Service View
@login_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'service_detail.html', {'service': service})

# Update Service View
@login_required
def update_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully.')
            return redirect('service_detail', pk=service.pk)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'update_service.html', {'form': form, 'service': service})

# Delete Service View
@login_required
def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully.')
        return redirect('home')
    return render(request, 'delete_service.html', {'service': service})

# Subscription (Buy) View with Razorpay Integration
@login_required
def subscribe_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']

            # Calculate total price with GST (if applicable)
            gst = 0.18 * service.service_price  # 18% GST
            total_amount = service.service_price + gst
            amount_in_paise = int(total_amount * 100)  # Convert to paise

            # Create Razorpay Order
            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': '1'
            })

            context = {
                'form': form,
                'service': service,
                'order_id': razorpay_order['id'],  # Razorpay order ID
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,  # Razorpay key from settings
                'total_amount': total_amount,
                'amount_in_paise': amount_in_paise,
            }

            return render(request, 'confirm_payment.html', context)
    else:
        form = SubscriptionForm()

    return render(request, 'subscribe_service.html', {'form': form, 'service': service})

# Payment callback view for Razorpay
@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        try:
            # Get Razorpay payment details from the request
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            # Verify the payment signature
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            }

            result = razorpay_client.utility.verify_payment_signature(params_dict)

            if result is None:
                # Payment was successful, you can add additional subscription logic here
                messages.success(request, 'Payment was successful!')
                return JsonResponse({'status': 'Payment Successful'})
            else:
                return JsonResponse({'status': 'Payment Verification Failed'})
        except Exception as e:
            return JsonResponse({'status': 'Error', 'message': str(e)})
    return JsonResponse({'status': 'Invalid Request'})

