from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, doctor_slots, manage_slot

router = DefaultRouter()
router.register('appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
    path('doctors/<int:doctor_id>/slots/', doctor_slots, name='doctor-slots'),
    path('doctors/<int:doctor_id>/manage-slot/', manage_slot, name='manage-slot'),
]
