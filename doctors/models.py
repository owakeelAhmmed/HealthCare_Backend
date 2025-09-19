from django.db import models
from accounts.models import User

class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile"
    )
    specialization = models.CharField(max_length=100)
    experience = models.IntegerField()
    bio = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    available_days = models.CharField(max_length=100, default="Monday,Tuesday,Wednesday,Thursday,Friday")
    available_time_start = models.TimeField(default="09:00:00")
    available_time_end = models.TimeField(default="17:00:00")
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

    @property
    def available_hours(self):
        return f"{self.available_time_start.strftime('%I:%M %p')} - {self.available_time_end.strftime('%I:%M %p')}"

    class Meta:
        ordering = ['user__first_name']