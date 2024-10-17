from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Service(models.Model):
    service_name = models.CharField(max_length=100)
    payment_terms = models.CharField(max_length=255)
    service_price = models.DecimalField(max_digits=10, decimal_places=2)
    service_package = models.CharField(max_length=255)
    service_tax = models.DecimalField(max_digits=5, decimal_places=2)
    service_image = models.ImageField(upload_to='services/')
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.service_name

class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link OTP to user
    otp_code = models.CharField(max_length=6)  # Store OTP code
    created_at = models.DateTimeField(auto_now_add=True)  # Track when the OTP was created

    def is_valid(self):
        """
        Check if the OTP is still valid based on the time of creation.
        Let's assume OTP is valid for 10 minutes.
        """
        expiration_time = self.created_at + timedelta(minutes=10)
        return timezone.now() < expiration_time

    def __str__(self):
        return f"OTP for {self.user.username}: {self.otp_code}"
