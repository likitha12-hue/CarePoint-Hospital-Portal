from django.contrib import admin

from .models import Appointment, Doctor, MedicalReport, Patient


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "specialization", "consultation_fee", "is_active")
    list_filter = ("department", "is_active")
    search_fields = ("name", "specialization")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "date_of_birth")
    search_fields = ("user__username", "phone")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "date", "time_slot", "status", "created_at")
    list_filter = ("status", "date", "doctor__department")
    list_editable = ("status",)


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ("appointment", "created_at")
