from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

DEPARTMENTS = [
    ("Cardiology", "Cardiology"),
    ("Pediatrics", "Pediatrics"),
    ("Orthopedics", "Orthopedics"),
    ("Neurology", "Neurology"),
]

TIME_SLOTS = [
    ("09:00 AM", "09:00 AM"),
    ("10:00 AM", "10:00 AM"),
    ("11:00 AM", "11:00 AM"),
    ("12:00 PM", "12:00 PM"),
    ("02:00 PM", "02:00 PM"),
    ("03:00 PM", "03:00 PM"),
    ("04:00 PM", "04:00 PM"),
    ("05:00 PM", "05:00 PM"),
]

# Python's date.weekday(): Monday = 0 ... Sunday = 6
DAY_NUMBERS = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50, choices=DEPARTMENTS)
    specialization = models.CharField(max_length=100)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2)
    available_days = models.CharField(
        max_length=50,
        default="Mon,Tue,Wed,Thu,Fri",
        help_text="Comma separated, e.g. Mon,Wed,Fri",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Dr. {self.name} ({self.department})"

    @property
    def initials(self):
        parts = self.name.replace("Dr.", "").split()
        return "".join(p[0] for p in parts[:2]).upper()

    @property
    def icon(self):
        return {
            "Cardiology": "bi-heart-pulse",
            "Pediatrics": "bi-emoji-smile",
            "Orthopedics": "bi-person-walking",
            "Neurology": "bi-lightning-charge",
        }.get(self.department, "bi-hospital")

    def available_day_list(self):
        return [d.strip().title() for d in self.available_days.split(",") if d.strip()]

    def available_weekday_numbers(self):
        return [DAY_NUMBERS[d] for d in self.available_day_list() if d in DAY_NUMBERS]


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Appointment(models.Model):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time_slot"]
        constraints = [
            # Database-level protection against double booking.
            # Cancelled appointments don't block the slot.
            models.UniqueConstraint(
                fields=["doctor", "date", "time_slot"],
                condition=~Q(status="Cancelled"),
                name="unique_active_doctor_slot",
            )
        ]

    def __str__(self):
        return f"{self.patient} -> {self.doctor.name} on {self.date} {self.time_slot}"

    @property
    def badge_class(self):
        return {
            self.PENDING: "warning text-dark",
            self.CONFIRMED: "primary",
            self.COMPLETED: "success",
            self.CANCELLED: "danger",
        }[self.status]


class MedicalReport(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="report")
    diagnosis = models.TextField()
    prescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.appointment}"
