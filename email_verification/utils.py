import hashlib
import secrets
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

DEFAULT_TTL_MIN = getattr(settings, 'EMAIL_CODE_TTL_MINUTES', 10)
MAX_ATTEMPTS = getattr(settings, 'EMAIL_CODE_MAX_ATTEMPTS', 5)
RESEND_COOLDOWN = getattr(settings, 'EMAIL_CODE_RESEND_COOLDOWN_SECONDS', 60)
SECRET = getattr(settings, 'EMAIL_CODE_SECRET', 'DEV-CHANGE-ME')

def gen_code():
    return f"{secrets.randbelow(900000) + 100000}"

def hash_code(code: str, email: str) -> str:
    s = f"{code}|{email.lower()}|{SECRET}".encode()
    return hashlib.sha256(s).hexdigest()

def send_code_email(email: str, code: str):
    subject = 'Tu código de verificación'
    context = {'code': code, 'ttl': DEFAULT_TTL_MIN}
    html = render_to_string('email_verification/email_code.html', context)
    text = f"Tu código es {code}. Vence en {DEFAULT_TTL_MIN} minutos."

    msg = EmailMultiAlternatives(subject, text, to=[email])
    msg.attach_alternative(html, 'text/html')
    msg.send()

def now_plus_minutes(m: int):
    return timezone.now() + timezone.timedelta(minutes=m)
