from .base import *

DEBUG = False

ALLOWED_HOSTS = ["*"]
SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASES = {
     "default": dj_database_url.parse(os.environ.get("DATABASE_URL"))
}
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


