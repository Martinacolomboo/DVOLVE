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
    historial_precio = models.ForeignKey('HistorialPrecioPlan', null=True, blank=True, on_delete=models.SET_NULL, help_text="Registro de precio vigente al momento del pago")
    def __str__(self):
        return f"{self.email} - {self.monto} ({self.estado})"

class PlanPrecio(models.Model):
    PLANES = [
        ('Mensual', 'Plan Mensual'),
        ('Trimestral', 'Plan Trimestral'),
    ]
    nombre = models.CharField(max_length=50, choices=PLANES, unique=True)
    precio_ars = models.DecimalField(max_digits=10, decimal_places=2)
    dias_vigencia = models.IntegerField(help_text="Cantidad de días que el usuario tendrá acceso al plan desde la fecha de compra.")
    descripcion = models.TextField(blank=True, null=True)
    es_descuento = models.BooleanField(default=False, help_text="¿Este plan tiene un descuento activo?")
    activo = models.BooleanField(default=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.nombre} - ${self.precio_ars} ARS"

class HistorialPrecioPlan(models.Model):
    plan = models.CharField(max_length=50)
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(default=timezone.now)
    descripcion = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.plan}: {self.precio_anterior} → {self.precio_nuevo} el {self.fecha.strftime('%d/%m/%Y %H:%M')}"
