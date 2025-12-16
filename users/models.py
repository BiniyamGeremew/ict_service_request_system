from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models

class CustomUser(AbstractUser):

    department = models.CharField(max_length=100, blank=True, null=True)
    staff_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username}"
    
User = get_user_model()

class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    target_group = models.CharField(
        max_length=50,
        choices=[
            ('admin', 'Admin'),
            ('staff', 'Staff'),
            ('technician', 'Technician'),
            ('manager', 'Manager')
        ],
        blank=True, null=True
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.target_group} - {self.message}"
