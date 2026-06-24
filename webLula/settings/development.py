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

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'DVOLVE <dvolveprogram@gmail.com>')
# EN development.py (pegá esto al final)

# Configuración SMTP para envío real de mails (Gmail)
