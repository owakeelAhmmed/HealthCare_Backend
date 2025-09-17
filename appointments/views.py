from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Appointment, CustomSlot
from .serializers import AppointmentSerializer
from doctors.models import Doctor
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta
from rest_framework import status



class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()

    def get_queryset(self):
        user = self.request.user

       
        if not user.is_authenticated:
            return Appointment.objects.none()

        
        if user.user_type == 1:
            return Appointment.objects.filter(patient=user)

        
        elif user.user_type == 2:
            return Appointment.objects.filter(doctor__user=user)

        
        elif user.user_type == 3:
            return Appointment.objects.all()

       
        return Appointment.objects.none()

    def perform_create(self, serializer):
        
        if self.request.user.user_type != 1:
            raise PermissionDenied("Only patients can create appointments.")
        serializer.save(patient=self.request.user)


@api_view(["GET"])
@permission_classes([AllowAny])  # slot দেখতে login লাগবে না
def doctor_slots(request, doctor_id):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    slot_duration = timedelta(minutes=30)  # প্রতি slot 30 মিনিট
    slots = []
    today = datetime.now().date()

    for day_offset in range(int(doctor.available_days)):
        current_date = today + timedelta(days=day_offset)
        start_time = datetime.combine(current_date, doctor.available_time_start)
        end_time = datetime.combine(current_date, doctor.available_time_end)

        while start_time + slot_duration <= end_time:
            slot_str = start_time.strftime("%Y-%m-%d %H:%M")

            # already booked হলে বাদ
            if not Appointment.objects.filter(
                doctor=doctor,
                date=current_date,
                time=start_time.time()
            ).exists():
                slots.append(slot_str)

            start_time += slot_duration

    return Response({
        "doctor": doctor.id,
        "slots": slots
    })


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

    # 1️⃣ Loop through available days range
    for day_offset in range(int(doctor.available_days)):
        current_date = today + timedelta(days=day_offset)
        start_time = datetime.combine(current_date, doctor.available_time_start)
        end_time = datetime.combine(current_date, doctor.available_time_end)

        # 2️⃣ Generate slots in range
        while start_time + slot_duration <= end_time:
            slot_time = start_time.time()

            # 3️⃣ Check manual override (CustomSlot)
            custom_slot = CustomSlot.objects.filter(
                doctor=doctor,
                date=current_date,
                time=slot_time
            ).first()

            if custom_slot:
                if not custom_slot.is_available:  # Blocked slot
                    start_time += slot_duration
                    continue

            # 4️⃣ Skip if already booked
            if Appointment.objects.filter(
                doctor=doctor,
                date=current_date,
                time=slot_time
            ).exists():
                start_time += slot_duration
                continue

            # 5️⃣ Add slot
            slots.append(f"{current_date} {slot_time.strftime('%H:%M')}")
            start_time += slot_duration

    return Response({
        "doctor": doctor.id,
        "slots": slots
    })


@api_view(["POST"])
@permission_classes([AllowAny])  # প্রয়োজনে IsAuthenticated + role check দেবে
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

    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    time = datetime.strptime(time_str, "%H:%M").time()

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