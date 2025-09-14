from django.db import models
from django.utils import timezone

class EmailVerification(models.Model):
    email = models.EmailField(db_index=True)
    code_hash = models.CharField(max_length=64)  # sha256
    attempts_left = models.PositiveSmallIntegerField(default=5)
    sent_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['email', 'expires_at'])]
        verbose_name = 'Verificación de email'
        verbose_name_plural = 'Verificaciones de email'

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_verified(self):
        return self.verified_at is not None

    def mark_verified(self):
        self.verified_at = timezone.now()
        self.save(update_fields=['verified_at'])
