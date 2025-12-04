from .base import *
import os
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = ["*"]

# ✅ USAMOS LA MISMA KEY QUE EN base.py
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True
    )
}

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ✅ Credenciales por variables de entorno
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
