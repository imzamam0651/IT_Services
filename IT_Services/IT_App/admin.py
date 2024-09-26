from django.contrib import admin
from .models import Service
# Register your models here.
class ServiceAdmin(admin.ModelAdmin):

    class Meta:
        model = Service

admin.site.register(Service, ServiceAdmin)