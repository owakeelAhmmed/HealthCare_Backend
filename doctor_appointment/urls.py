from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from appointments import views as appointment_views
from doctors import views as doctor_views
from accounts import views as account_views

router = routers.DefaultRouter()
router.register('appointments', appointment_views.AppointmentViewSet)
router.register('doctors', doctor_views.DoctorViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # Djoser authentication URLs
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api/', include('appointments.urls')),
]
