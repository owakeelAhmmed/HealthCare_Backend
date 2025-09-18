from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta

from .models import Appointment, CustomSlot
from .serializers import AppointmentSerializer
from doctors.models import Doctor


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Appointment.objects.none()

        if user.user_type == 1:  # Patient
            return Appointment.objects.filter(patient=user)

        elif user.user_type == 2:  # Doctor
            return Appointment.objects.filter(doctor__user=user)

        elif user.user_type == 3:  # Admin
            return Appointment.objects.all()

        return Appointment.objects.none()

    def perform_create(self, serializer):
        if self.request.user.user_type != 1:
            raise PermissionDenied("Only patients can create appointments.")
        serializer.save(patient=self.request.user)
    
    def perform_update(self, serializer):
        print("Incoming data:", self.request.data)
        instance = serializer.instance
        user = self.request.user

        if user.user_type == 1 and instance.patient == user:
            # patient তার own appointment এর status update করতে পারবে
            serializer.save()
        elif user.user_type in [2, 3]:
            serializer.save()
        else:
            raise PermissionDenied("You cannot update this appointment.")



@api_view(["GET"])
@permission_classes([AllowAny])
def doctor_slots(request, doctor_id):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    slot_duration = timedelta(minutes=30)
    slots = []
    today = datetime.now().date()

    # doctor.available_days string কে list এ convert
    available_days = [day.strip() for day in doctor.available_days.split(",")]

    # আজ থেকে 7 দিন check করবো (তুমি চাইলে range বাড়াতে পারো)
    for day_offset in range(7):
        current_date = today + timedelta(days=day_offset)

        # আজকের দিনটা যদি doctor's available_days এ না থাকে → skip
        if current_date.strftime("%A") not in available_days:
            continue  

        start_time = datetime.combine(current_date, doctor.available_time_start)
        end_time = datetime.combine(current_date, doctor.available_time_end)

        while start_time + slot_duration <= end_time:
            slot_time = start_time.time()

            # CustomSlot check
            custom_slot = CustomSlot.objects.filter(
                doctor=doctor,
                date=current_date,
                time=slot_time
            ).first()
            if custom_slot and not custom_slot.is_available:
                start_time += slot_duration
                continue

            # Already booked হলে skip
            if Appointment.objects.filter(
                doctor=doctor,
                date=current_date,
                time=slot_time
            ).exists():
                start_time += slot_duration
                continue

            # Valid slot যোগ করো
            slots.append(f"{current_date} {slot_time.strftime('%H:%M')}")
            start_time += slot_duration

    return Response({
        "doctor": doctor.id,
        "slots": slots
    })



@api_view(["POST"])
@permission_classes([IsAuthenticated])  # doctor/admin slot manage করবে
def manage_slot(request, doctor_id):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    date_str = request.data.get("date")
    time_str = request.data.get("time")
    is_available = request.data.get("is_available", True)

    if not date_str or not time_str:
        return Response({"error": "Date and Time are required"}, status=400)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return Response({"error": "Invalid date or time format"}, status=400)

    slot, created = CustomSlot.objects.update_or_create(
        doctor=doctor,
        date=date,
        time=time,
        defaults={"is_available": is_available}
    )

    return Response({
        "message": "Slot updated" if not created else "Slot created",
        "slot": f"{date} {time.strftime('%H:%M')}",
        "is_available": is_available
    }, status=status.HTTP_200_OK)
