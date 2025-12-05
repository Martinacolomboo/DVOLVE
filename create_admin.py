import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webLula.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.getenv("ADMIN_USER")
password = os.getenv("ADMIN_PASS")

if not username or not password:
    print("❌ Faltan credenciales en variables de entorno (ADMIN_USER / ADMIN_PASS)")
    exit()

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password)
    print(f"✔ Superusuario '{username}' creado en producción.")
else:
    print(f"ℹ El usuario '{username}' ya existe.")
