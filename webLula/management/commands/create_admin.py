import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Crea un superusuario usando variables de entorno en Render"

    def handle(self, *args, **kwargs):
        username = os.environ.get("DJANGO_SU_NAME")
        email = os.environ.get("DJANGO_SU_EMAIL")
        password = os.environ.get("DJANGO_SU_PASSWORD")

        if not username or not password:
            self.stdout.write(self.style.ERROR("Faltan variables de entorno para crear admin"))
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superusuario creado: {username}"))
        else:
            self.stdout.write(self.style.WARNING("El superusuario ya existe"))
