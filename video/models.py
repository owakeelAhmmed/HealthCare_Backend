from django.db import models
from accounts.models import User
from doctors.models import Doctor
from appointments.models import Appointment

class VideoCallSession(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='video_session')
    room_id = models.CharField(max_length=100, unique=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Video Session: {self.room_id}"