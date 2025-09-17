# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Patient'),
        (2, 'Doctor'),
        (3, 'Admin'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.username
