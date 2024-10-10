from django.urls import path
from . import views

urlpatterns = [
    # User-related views
    path('register/', views.register, name='register'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('login/', views.user_login, name='login'),
    
    # Service CRUD views
    path('', views.home, name='home'),  # Home page showing active services
    path('service/create/', views.create_service, name='create_service'),  # Create a service
    path('service/<int:pk>/', views.service_detail, name='service_detail'),  # Single service view
    path('service/<int:pk>/update/', views.update_service, name='update_service'),  # Update a service
    path('service/<int:pk>/delete/', views.delete_service, name='delete_service'),  # Delete a service
    path('services/', views.service_list, name='service_list'),  # List all services
    
    # Subscription and Razorpay integration views
    path('service/<int:pk>/subscribe/', views.subscribe_service, name='subscribe_service'),  # Subscribe to a service
    path('payment/callback/', views.payment_callback, name='payment_callback'),  # Razorpay payment callback
]
