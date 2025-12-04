from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    ".fly.dev",
    "tu-dominio.com",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            "sslmode": "require",
        },
    }
}


# Cloudflare R2
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("R2_BUCKET")
AWS_S3_ENDPOINT_URL = os.getenv("R2_URL")
AWS_S3_REGION_NAME = "auto"
AWS_S3_SIGNATURE_VERSION = "s3v4"
