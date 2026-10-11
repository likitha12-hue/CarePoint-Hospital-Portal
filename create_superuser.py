"""Creates an admin user on Render from environment variables (safe to run many times)."""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital_project.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username, os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com"), password
    )
    print(f"Superuser '{username}' created.")
else:
    print("Superuser step skipped (already exists or no password set).")
