from django.shortcuts import render
from frontend.models import SiteConfiguration

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 1. LISTA BLANCA: Rutas que SIEMPRE pasan (incluso en mantenimiento)
        # Agregamos '/frontend/' porque esa es tu URL de login
        if path.startswith('/admin/') or \
           path.startswith('/frontend/panel-admin/') or \
           path == '/frontend/' or \
           path.startswith('/frontend/login/') or \
           path.startswith('/frontend/registro/') or \
           path.startswith('/clientes/logout/') or \
           path.startswith('/static/') or \
           path.startswith('/media/'):
            return self.get_response(request)

        # 2. Verificar si el Mantenimiento está activo
        try:
            config = SiteConfiguration.objects.first()
            is_maintenance = config.is_maintenance_mode if config else False
        except:
            is_maintenance = False

        # 3. BLOQUEO
        if is_maintenance:
            # Si es Admin, pasa siempre
            if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
                return self.get_response(request)
            
            # Si es usuario común -> PANTALLA DE MANTENIMIENTO
            return render(request, 'frontend/mantenimiento.html')

        return self.get_response(request)