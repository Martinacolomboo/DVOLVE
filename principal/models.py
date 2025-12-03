from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User


class VerifiedEmail(models.Model):
    email = models.EmailField(unique=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    vencimiento = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.email

class Pago(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, default='ARS')
    plataforma = models.CharField(max_length=20)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default="exitoso")
    payment_id_externo = models.CharField(max_length=100, blank=True, null=True)
    
    # HISTORIAL: Qué compró
    tipo_plan = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return f"{self.email} - {self.monto} ({self.estado})"
