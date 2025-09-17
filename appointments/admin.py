from django.contrib import admin
from .models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'time', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'date', 'doctor')
    search_fields = ('patient__username', 'doctor__user__username', 'reason')
    ordering = ('-date', '-time')

admin.site.register(Appointment, AppointmentAdmin)
