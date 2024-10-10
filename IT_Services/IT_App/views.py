from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import razorpay
from .models import Service
from .forms import UserRegistrationForm, OTPVerificationForm, ServiceForm, SubscriptionForm

# Razorpay client initialization
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Home view to list all active services
@login_required
def home(request):
    services = Service.objects.filter(active=True)  # Only show active services
    return render(request, 'home.html', {'services': services})

# User registration view (assumed pre-existing)
def register(request):
    # Logic for user registration and OTP verification
    pass

# OTP verification view (assumed pre-existing)
def otp_verification(request):
    # Logic for OTP verification
    pass

# Login view (assumed pre-existing)
def user_login(request):
    # Logic for user login
    pass

# View to handle service creation
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

# View to handle service update
@login_required
def update_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('service_detail', pk=service.pk)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'update_service.html', {'form': form})

# View to handle service deletion
@login_required
def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('service_list')
    return render(request, 'delete_service.html', {'service': service})

# View to display a single service
@login_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'service_detail.html', {'service': service})

# View to list all services
@login_required
def service_list(request):
    services = Service.objects.all()  # You can filter this list as needed
    return render(request, 'service_list.html', {'services': services})

# View to subscribe to a service (with Razorpay integration)
@login_required
def subscribe_service(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('address')

            # Calculate net price with GST
            service_price = service.service_price
            service_tax = service.service_tax
            total_amount = service_price + (service_price * service_tax / 100)

            # Convert amount to paise (Razorpay requires amount in paise)
            amount_in_paise = int(total_amount * 100)

            # Create Razorpay Order
            razorpay_order = razorpay_client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "payment_capture": "1",  # Auto-capture payment after success
            })

            # Pass order ID and details to template
            context = {
                'form': form,
                'service': service,
                'order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
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
