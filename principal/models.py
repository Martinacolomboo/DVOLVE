from django.db import models

from django.db import models

class VerifiedEmail(models.Model):
    email = models.EmailField(unique=True)
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Pago(models.Model):
    email = models.EmailField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default="pendiente")  # puede ser 'exitoso' o 'cancelado'

    def __str__(self):
        return f"{self.email} - {self.monto} ({self.estado})"
