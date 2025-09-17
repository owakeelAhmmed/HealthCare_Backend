from django.contrib import admin
from .models import Doctor

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'specialization', 'experience', 'consultation_fee', 'available_days', 'available_time_start', 'available_time_end')
    list_filter = ('specialization', 'available_days')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')
    ordering = ('id',)

admin.site.register(Doctor, DoctorAdmin)
