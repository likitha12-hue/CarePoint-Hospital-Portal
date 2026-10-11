from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "hospital"

urlpatterns = [
    path("", views.doctor_list, name="doctor_list"),
    path("book/", views.book_appointment, name="book"),
    path("api/slots/", views.available_slots, name="slots"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("appointments/<int:pk>/cancel/", views.cancel_appointment, name="cancel"),
    path("staff/appointments/", views.staff_appointments, name="staff_appointments"),
    path("staff/appointments/<int:pk>/status/", views.update_status, name="update_status"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="hospital/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
