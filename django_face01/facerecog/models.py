from django.db import models
from django.contrib.auth.models import AbstractUser

class Person(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=15)
    faceimage = models.ImageField(upload_to='face_images/')
    face_encode = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    MANAGER = 'manager'
    CASHIER = 'cashier'
    ROLE_CHOICES = [
        (MANAGER, 'Manager'),
        (CASHIER, 'Cashier'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CASHIER)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    photo_profile = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.username
