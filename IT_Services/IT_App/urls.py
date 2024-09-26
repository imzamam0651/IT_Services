from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('login/', views.user_login, name='login'),
    path('home/', views.home, name='home'),  # Home page with active services
    path('services/<int:pk>/subscribe/', views.subscribe_service, name='subscribe_service'),  # Subscribe page

# Service CRUD URLs
    path('services/', views.service_list, name='service_list'),  # List all services
    path('services/create/', views.create_service, name='create_service'),  # Create new service
    path('services/<int:pk>/', views.service_detail, name='service_detail'),  # View single service
    path('services/<int:pk>/update/', views.update_service, name='update_service'),  # Update service
    path('services/<int:pk>/delete/', views.delete_service, name='delete_service'),  # Delete service

]
