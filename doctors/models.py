# doctors/models.py
from django.db import models
from accounts.models import User

class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # user ডিলিট হলে doctor ডিলিট হবে
        related_name="doctor_profile"
    )
    specialization = models.CharField(max_length=100)
    experience = models.IntegerField()
    bio = models.TextField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    available_days = models.CharField(max_length=100)  # Comma separated days
    available_time_start = models.TimeField()
    available_time_end = models.TimeField()

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
