from django.db import models
from django.contrib.auth.models import AbstractUser


GENDER_SELECTION = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('NS', 'Not Specified'),
]


class User(AbstractUser):
    # We don't need to define the email attribute because is inherited from AbstractUser
    gender = models.CharField(max_length=20, choices=GENDER_SELECTION, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=1000, blank=True)
    specialty = models.JSONField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True)
