import os
from django.contrib.auth.models import User

def create_superuser_if_not_exists():
    username = os.environ.get("DJANGO_SU_NAME")
    email = os.environ.get("DJANGO_SU_EMAIL")
    password = os.environ.get("DJANGO_SU_PASSWORD")

    if username and password:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"Superusuario creado: {username}")
        else:
            print("Superusuario ya existía. No se creó.")
    else:
        print("Variables de entorno de admin no configuradas.")
