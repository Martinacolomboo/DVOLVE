from .base import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lula',
        'USER': 'postgres',
        'PASSWORD': 'hola',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
# EN development.py (pegá esto al final)

# Configuración SMTP para envío real de mails (Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # <--- ESTO ES IMPORTANTE
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'dvolveprogram@gmail.com'
EMAIL_HOST_PASSWORD = 'kvtk wczt hnca anaj'  # <--- Tu clave de aplicación (la separé por las dudas)
DEFAULT_FROM_EMAIL = 'DVOLVE <dvolveprogram@gmail.com>'
