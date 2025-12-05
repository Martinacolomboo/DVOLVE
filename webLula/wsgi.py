"""
WSGI config for webLula project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from frontend.utils.create_superuser import create_superuser_if_not_exists

# crea admin automáticamente si no existe
create_superuser_if_not_exists()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webLula.settings.production')

application = get_wsgi_application()
