from django.db import models
from django.contrib.auth.models import AbstractUser

class Person(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=15)
    faceimage = models.ImageField(upload_to='face_images/', blank=True, null=True)
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
    name = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CASHIER)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    photo_profile = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Add related_name to prevent clashes
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Add related_name to prevent clashes
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username
