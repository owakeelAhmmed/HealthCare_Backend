# appointments/models.py
from django.db import models
from accounts.models import User
from doctors.models import Doctor
from datetime import datetime


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('paid', 'Paid'),
    )

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # patient ডিলিট হলে তার সব appointment ডিলিট হবে
        related_name='patient_appointments'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,  # doctor ডিলিট হলে তার সব appointment ডিলিট হবে
        related_name='doctor_appointments'
    )
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def slot_datetime(self):
        return datetime.combine(self.date, self.time)

    def __str__(self):
        return f"Appointment: {self.patient.username} with Dr. {self.doctor.user.last_name} on {self.date}"
    

class CustomSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="custom_slots")
    date = models.DateField()
    time = models.TimeField()
    is_available = models.BooleanField(default=True)  # False হলে block slot

    class Meta:
        unique_together = ('doctor', 'date', 'time')

    def __str__(self):
        status = "Available" if self.is_available else "Blocked"
        return f"{self.date} {self.time} - {status}"