from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Appointment, Doctor


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label="Full name")
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, label="Phone number")

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["doctor", "date", "time_slot", "reason"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time_slot": forms.HiddenInput(),  # filled by the JavaScript slot picker
            "reason": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "doctor": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True)

    def clean_date(self):
        chosen = self.cleaned_data["date"]
        if chosen < date.today():
            raise forms.ValidationError("You cannot book an appointment in the past.")
        return chosen

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get("doctor")
        chosen_date = cleaned.get("date")
        slot = cleaned.get("time_slot")

        if doctor and chosen_date:
            if chosen_date.weekday() not in doctor.available_weekday_numbers():
                raise forms.ValidationError(
                    f"Dr. {doctor.name} is only available on: {doctor.available_days}."
                )
            if slot and Appointment.objects.filter(
                doctor=doctor, date=chosen_date, time_slot=slot
            ).exclude(status=Appointment.CANCELLED).exists():
                raise forms.ValidationError(
                    "That slot is already booked. Please choose another one."
                )
        return cleaned
