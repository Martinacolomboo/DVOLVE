from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods


from .forms import RequestCodeForm, VerifyCodeForm
from .models import EmailVerification
from .utils import (
    gen_code, hash_code, send_code_email, now_plus_minutes,
    MAX_ATTEMPTS, RESEND_COOLDOWN, DEFAULT_TTL_MIN
)

def _client_ip(request):
    return request.META.get('REMOTE_ADDR')

@require_http_methods(["GET", "POST"])
def request_code_view(request):
    monto = request.GET.get("monto")
    print("🟦 GET monto recibido:", monto)
    if monto:
        try:
            request.session["monto"] = float(monto)
            request.session.modified = True  # fuerza el guardado inmediato
            print("🟩 Monto guardado en sesión:", request.session.get("monto"))
        except ValueError:
            print("⚠️ Valor de monto no numérico:", monto)
    if request.method == 'POST':
        form = RequestCodeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            ip = _client_ip(request)

            last = (EmailVerification.objects
                    .filter(email=email)
                    .order_by('-sent_at')
                    .first())
            if last and (timezone.now() - last.sent_at).total_seconds() < RESEND_COOLDOWN:
                wait = int(RESEND_COOLDOWN - (timezone.now() - last.sent_at).total_seconds())
                messages.error(request, f"Esperá {wait}s para reenviar el código.")
                return redirect('email_verification:request')

            code = gen_code()
            EmailVerification.objects.create(
                email=email,
                code_hash=hash_code(code, email),
                attempts_left=MAX_ATTEMPTS,
                sent_at=timezone.now(),
                expires_at=now_plus_minutes(DEFAULT_TTL_MIN),
                ip_address=ip,
            )
            send_code_email(email, code)
            request.session['ev_email'] = email
            messages.success(request, 'Código enviado. Revisá tu correo.')
            return redirect('email_verification:verify')
    else:
        initial_email = request.session.get('ev_email')
        form = RequestCodeForm(initial={'email': initial_email})

    return render(request, 'email_verification/request.html', {'form': form})


@require_http_methods(["GET", "POST"])
def verify_code_view(request):
    email = request.session.get('ev_email')
    if request.method == 'POST':
        email = (request.POST.get('email') or email or '').lower()
        form = VerifyCodeForm(request.POST)

        if not email:
            messages.error(request, 'Falta el email. Volvé a solicitar código.')
            return redirect('email_verification:request')

        if form.is_valid():
            code = form.cleaned_data['code']
            rec = (EmailVerification.objects
                   .filter(email=email)
                   .order_by('-sent_at')
                   .first())
            if not rec:
                messages.error(request, 'Solicitá un código primero.')
                return redirect('email_verification:request')

            if rec.is_expired():
                messages.error(request, 'El código venció. Pedí uno nuevo.')
                return redirect('email_verification:request')

            if rec.attempts_left <= 0:
                messages.error(request, 'Demasiados intentos. Pedí un código nuevo.')
                return redirect('email_verification:request')

            if hash_code(code, email) != rec.code_hash:
                rec.attempts_left -= 1
                rec.save(update_fields=['attempts_left'])
                messages.error(request, f"Código incorrecto. Intentos restantes: {rec.attempts_left}")
                return redirect('email_verification:verify')

            # ÉXITO
            rec.mark_verified()
            request.session['email_verified'] = True
            request.session['email_verified_address'] = email
            request.session['checkout_email'] = email   
            from principal.models import VerifiedEmail
            VerifiedEmail.objects.get_or_create(email=email)

            monto = request.session.get("monto") or 0
            return redirect(f"/checkout/?monto={monto}") 
    else:
        form = VerifyCodeForm()

    return render(request, 'email_verification/verify.html', {
        'form': form,
        'email': email,
    })
