from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AppointmentForm, RegisterForm
from .models import DEPARTMENTS, TIME_SLOTS, Appointment, Doctor, Patient


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


# ---------- Doctors ----------
def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True)
    dept = request.GET.get("department", "")
    q = request.GET.get("q", "").strip()
    if dept:
        doctors = doctors.filter(department=dept)
    if q:
        doctors = doctors.filter(Q(name__icontains=q) | Q(specialization__icontains=q))
    return render(request, "hospital/doctor_list.html", {
        "doctors": doctors,
        "departments": [d[0] for d in DEPARTMENTS],
        "selected_dept": dept,
        "q": q,
    })


# ---------- Register ----------
def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Patient.objects.create(user=user, phone=form.cleaned_data["phone"])
        login(request, user)
        messages.success(request, "Account created. Welcome!")
        return redirect("hospital:doctor_list")
    return render(request, "hospital/register.html", {"form": form})


# ---------- Booking ----------
@login_required
def book_appointment(request):
    patient, _ = Patient.objects.get_or_create(user=request.user)
    initial = {}
    if request.GET.get("doctor"):
        initial["doctor"] = request.GET["doctor"]

    form = AppointmentForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        appt = form.save(commit=False)
        appt.patient = patient
        try:
            appt.save()
        except IntegrityError:  # two people clicked at the same moment
            form.add_error(None, "That slot was just taken. Please pick another.")
        else:
            messages.success(request, "Appointment requested! Waiting for confirmation.")
            return redirect("hospital:dashboard")
    doctors = Doctor.objects.filter(is_active=True)
    return render(request, "hospital/book_appointment.html", {
        "form": form,
        "doctors": doctors,
        "departments": [d[0] for d in DEPARTMENTS],
        "selected_doctor": str(form["doctor"].value() or ""),
    })


def available_slots(request):
    """JSON used by the JavaScript slot picker."""
    doctor = get_object_or_404(Doctor, pk=request.GET.get("doctor"), is_active=True)
    try:
        chosen = date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        return JsonResponse({"error": "Invalid date"}, status=400)

    works_that_day = chosen.weekday() in doctor.available_weekday_numbers()
    booked = list(
        Appointment.objects.filter(doctor=doctor, date=chosen)
        .exclude(status=Appointment.CANCELLED)
        .values_list("time_slot", flat=True)
    )
    return JsonResponse({
        "works_that_day": works_that_day,
        "slots": [{"time": t[0], "booked": t[0] in booked} for t in TIME_SLOTS],
    })


# ---------- Patient dashboard ----------
@login_required
def dashboard(request):
    patient, _ = Patient.objects.get_or_create(user=request.user)
    today = date.today()
    mine = patient.appointments.select_related("doctor")
    upcoming = mine.filter(date__gte=today).exclude(status__in=["Completed", "Cancelled"])
    past = mine.exclude(pk__in=upcoming.values("pk")).order_by("-date")
    return render(request, "hospital/dashboard.html", {
        "upcoming": upcoming,
        "past": past,
        "completed_count": mine.filter(status="Completed").count(),
        "cancelled_count": mine.filter(status="Cancelled").count(),
    })


@login_required
@require_POST
def cancel_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, patient__user=request.user)
    if appt.status in (Appointment.PENDING, Appointment.CONFIRMED):
        appt.status = Appointment.CANCELLED
        appt.save()
        messages.info(request, "Appointment cancelled.")
    else:
        messages.error(request, "This appointment can no longer be cancelled.")
    return redirect("hospital:dashboard")


# ---------- Staff ----------
@user_passes_test(is_staff_user, login_url="hospital:login")
def staff_appointments(request):
    status = request.GET.get("status", "")
    appts = Appointment.objects.select_related("patient__user", "doctor")
    if status:
        appts = appts.filter(status=status)
    return render(request, "hospital/staff_appointments.html", {
        "appointments": appts.order_by("-date"),
        "statuses": [s[0] for s in Appointment.STATUS_CHOICES],
        "selected_status": status,
        "counts": {s[0]: Appointment.objects.filter(status=s[0]).count() for s in Appointment.STATUS_CHOICES},
    })


@user_passes_test(is_staff_user, login_url="hospital:login")
@require_POST
def update_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get("status")
    if new_status in dict(Appointment.STATUS_CHOICES):
        try:
            appt.status = new_status
            appt.save()
            messages.success(request, f"Appointment #{appt.pk} marked {new_status}.")
        except IntegrityError:
            messages.error(request, "Another active booking already uses that slot.")
    else:
        messages.error(request, "Invalid status.")
    return redirect("hospital:staff_appointments")
