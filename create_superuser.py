import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webLula.settings")
django.setup()

from django.contrib.auth.models import User

username = os.getenv("ADMIN_USER")
email = os.getenv("ADMIN_EMAIL")
password = os.getenv("ADMIN_PASS")

if not username or not password:
    print("Faltan variables de entorno ADMIN_USER / ADMIN_PASS")
    exit()

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superusuario creado con éxito!")
else:
    print("El superusuario ya existe.")
