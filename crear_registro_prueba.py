from django.contrib.auth.models import User
from principal.models import Pago, HistorialPrecioPlan
from django.utils import timezone

# 1. Crear usuario de prueba (si no existe)
user, created = User.objects.get_or_create(username='prueba_admin', defaults={
    'email': 'prueba_admin@email.com',
    'is_staff': False,
    'is_superuser': False
})

# 2. Crear historial de precio de prueba (si no existe)
historial, created = HistorialPrecioPlan.objects.get_or_create(
    plan='Mensual',
    precio_nuevo=45000,
    defaults={
        'precio_anterior': 40000,
        'fecha': timezone.now(),
        'descripcion': 'Precio de prueba para test.'
    }
)

# 3. Crear pago de prueba
Pago.objects.create(
    user=user,
    email=user.email,
    monto=45000,
    moneda='ARS',
    plataforma='test',
    estado='exitoso',
    tipo_plan='Mensual',
    historial_precio=historial
)

print('¡Registro de prueba creado!')
