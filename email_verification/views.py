from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from .forms import RequestCodeForm, VerifyCodeForm
from .models import EmailVerification
from .utils import gen_code, hash_code, send_code_email, now_plus_minutes, DEFAULT_TTL_MIN, MAX_ATTEMPTS, RESEND_COOLDOWN
# IMPORTANTE: Importamos el modelo de suscripciones
from principal.models import VerifiedEmail 

def _client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

@require_http_methods(["GET", "POST"])
def request_code_view(request):
    monto = request.GET.get("monto")
    if monto:
        try:
            request.session["monto"] = float(monto)
        except ValueError: pass

    if request.method == 'POST':
        form = RequestCodeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            ip = _client_ip(request)

            # --- CASO 1: USUARIO YA VERIFICADO ---
            # Buscamos el objeto completo para ver sus fechas
            usuario_verif = VerifiedEmail.objects.filter(email=email).first()

            if usuario_verif:
                request.session['verified_email'] = email
                request.session['checkout_email'] = email
                request.session.pop('ev_email', None)
                
                # CHEQUEO INTELIGENTE: ¿Tiene plan activo?
                plan_activo = False
                fecha_vencimiento = None
                
                if usuario_verif.vencimiento and usuario_verif.vencimiento > timezone.now():
                    plan_activo = True
                    fecha_vencimiento = usuario_verif.vencimiento

                # A. Si venía de registrarse, lo dejamos pasar
                if request.session.get('verification_next'):
                    return redirect(request.session['verification_next'])
                
                # B. Si venía a pagar, le mostramos la situación real
                else:
                    return render(request, 'email_verification/request.html', {
                        'form': form,
                        'already_verified': True,
                        'email': email,
                        'plan_activo': plan_activo,       # <--- NUEVA VARIABLE
                        'vencimiento': fecha_vencimiento  # <--- NUEVA VARIABLE
                    })

            # --- CASO 2: NO VERIFICADO (Enviar código) ---
            # ... (Este bloque sigue igual que antes) ...
            last = EmailVerification.objects.filter(email=email).order_by('-sent_at').first()
            if last and (timezone.now() - last.sent_at).total_seconds() < RESEND_COOLDOWN:
                messages.error(request, "Esperá unos segundos para reenviar.")
                return redirect('email_verification:request')

            code = gen_code()
            EmailVerification.objects.create(
                email=email,
                code_hash=hash_code(code, email),
                attempts_left=MAX_ATTEMPTS,
                sent_at=timezone.now(),
                expires_at=now_plus_minutes(DEFAULT_TTL_MIN),
                ip_address=ip
            )
            send_code_email(email, code)
            request.session['ev_email'] = email
            return redirect('email_verification:verify')
            
    else:
        form = RequestCodeForm(initial={'email': request.session.get('ev_email')})
        
    return render(request, 'email_verification/request.html', {'form': form})
    
@require_http_methods(["GET", "POST"])
def verify_code_view(request):
    email = request.session.get('ev_email')
    if not email: return redirect('email_verification:request')

    # --- CÁLCULO DEL TIEMPO RESTANTE (ESTO FALTABA) ---
    resend_wait = 0
    last_sent = EmailVerification.objects.filter(email=email).order_by('-sent_at').first()
    
    if last_sent:
        elapsed = (timezone.now() - last_sent.sent_at).total_seconds()
        if elapsed < RESEND_COOLDOWN:
            resend_wait = int(RESEND_COOLDOWN - elapsed)
    # ---------------------------------------------------

    if request.method == 'POST':
        form = VerifyCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            # Usamos el objeto 'last_sent' que ya buscamos arriba
            rec = last_sent 

            if not rec or timezone.now() > rec.expires_at:
                messages.error(request, "Código expirado.")
            elif rec.attempts_left <= 0:
                messages.error(request, "Demasiados intentos.")
            elif rec.code_hash != hash_code(code, email):
                rec.attempts_left -= 1
                rec.save()
                messages.error(request, "Código incorrecto.")
            else:
                # ÉXITO
                rec.verified_at = timezone.now()
                rec.save()
                
                request.session['email_verified'] = True
                request.session['email_verified_address'] = email
                request.session['checkout_email'] = email
                
                VerifiedEmail.objects.get_or_create(email=email)

                next_url = request.session.pop('verification_next', None)
                if next_url:
                    return redirect(next_url)
                else:
                    monto = request.session.get("monto") or 0
                    url_destino = reverse('principal:metodos_pago')
                    return redirect(f"{url_destino}?monto={monto}")
    else:
        form = VerifyCodeForm()

    return render(request, 'email_verification/verify.html', {
        'form': form, 
        'email': email,
        'resend_wait': resend_wait  # <--- AHORA SÍ PASAMOS EL TIEMPO AL HTML
    })
# --- ESTA ES LA FUNCIÓN QUE TE FALTABA ---
@require_http_methods(["POST"])
def resend_code_view(request):
    """Reenvía el código al email guardado en sesión."""
    email = request.session.get('ev_email')
    if not email:
        return redirect('email_verification:request')

    # Chequeo de Cooldown
    last = EmailVerification.objects.filter(email=email).order_by('-sent_at').first()
    if last and (timezone.now() - last.sent_at).total_seconds() < RESEND_COOLDOWN:
        messages.error(request, "Por favor esperá unos segundos antes de reenviar.")
        return redirect('email_verification:verify')

    # Generar y enviar nuevo código
    code = gen_code()
    ip = _client_ip(request)
    EmailVerification.objects.create(
        email=email,
        code_hash=hash_code(code, email),
        attempts_left=MAX_ATTEMPTS,
        sent_at=timezone.now(),
        expires_at=now_plus_minutes(DEFAULT_TTL_MIN),
        ip_address=ip
    )
    send_code_email(email, code)
    messages.success(request, "Código reenviado con éxito.")
    
    return redirect('email_verification:verify')