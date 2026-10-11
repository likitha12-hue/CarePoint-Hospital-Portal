from django.core.management.base import BaseCommand

from hospital.models import Doctor

DOCTORS = [
    ("Ravi Kumar", "Cardiology", "Interventional Cardiologist", 800, "Mon,Tue,Wed,Thu,Fri"),
    ("Anita Sharma", "Cardiology", "Heart Failure Specialist", 700, "Mon,Wed,Fri,Sat"),
    ("Suresh Reddy", "Pediatrics", "Child Health Specialist", 500, "Mon,Tue,Wed,Thu,Fri,Sat"),
    ("Meena Iyer", "Pediatrics", "Neonatologist", 600, "Tue,Thu,Sat"),
    ("Arjun Mehta", "Orthopedics", "Joint Replacement Surgeon", 900, "Mon,Tue,Thu,Fri"),
    ("Kavya Nair", "Orthopedics", "Sports Injury Specialist", 750, "Mon,Wed,Fri"),
    ("Rahul Verma", "Neurology", "Neurologist", 850, "Mon,Tue,Wed,Thu,Fri"),
    ("Priya Das", "Neurology", "Stroke & Epilepsy Specialist", 950, "Tue,Wed,Sat"),
]


class Command(BaseCommand):
    help = "Adds sample doctors (safe to run many times)."

    def handle(self, *args, **options):
        created = 0
        for name, dept, spec, fee, days in DOCTORS:
            _, was_created = Doctor.objects.get_or_create(
                name=name,
                defaults=dict(department=dept, specialization=spec,
                              consultation_fee=fee, available_days=days),
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f"{created} doctors added, {Doctor.objects.count()} total."))
