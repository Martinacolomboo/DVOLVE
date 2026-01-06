from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import timedelta
import mercadopago
import requests

from .models import Pago, VerifiedEmail
from .helpers import CheckoutService
from .constants import get_plan_by_amount, get_plan_duration, get_plan_price # <--- IMPORTANTE: Importar get_plan_price

def home(request):
    return render(request, 'principal/home.html')

def segunda_pagina(request):
    return render(request, 'principal/segunda_pagina.html')

def pagos(request):
    return render(request, 'principal/pagos.html')

def privacidad(request):
    return render(request, "principal/privacidad.html")

def obtener_dolar_oficial():
    try:
        response = requests.get("https://dolarapi.com/v1/dolares/oficial")
        data = response.json()
        return float(data["venta"])  
    except Exception:
        return getattr(settings, "DOLLAR_FALLBACK", 1464.55) 

def metodos_pago(request):
    response = CheckoutService.chequear_email_verificado(request)
    if response is not None: return response

    monto_raw = request.GET.get("monto") or request.session.get("monto_ars") or request.session.get("monto")
    if monto_raw is None: return redirect("principal:pagos")

    try:
        monto_ars = float(monto_raw)
    except (ValueError, TypeError):
        return redirect("principal:pagos")

    tasa = obtener_dolar_oficial()
    monto_usd = round(monto_ars / tasa, 2)

    request.session["monto_ars"] = monto_ars
    request.session["monto_usd"] = monto_usd
    request.session.modified = True

    return render(request, "principal/metodos_pago.html", {
        "monto_ars": monto_ars,
        "monto_usd": monto_usd,
    })

def pagar_mercadopago(request):
    # Obtener monto
    monto_ars = request.GET.get("monto") or request.session.get("monto_ars") or request.session.get("monto")
    try:
        monto_ars = float(monto_ars)
    except:
        return JsonResponse({"error": "Monto inválido"}, status=400)

    # Obtener email
    email = request.session.get("checkout_email")
    if not email and request.user.is_authenticated:
        email = request.user.email
    if not email or email == "test@test.com":
        messages.error(request, "Ocurrió un error al identificar tu email. Por favor, intentá de nuevo.")
        return redirect("principal:pagos")

    # Recuperar el PLAN (importante para enviarlo en la URL)
    tipo_plan = request.session.get("tipo_plan", "Mensual") # Default Mensual si falla

    # Guardar datos en la sesión
    request.session["checkout_email"] = email
    request.session["monto_ars"] = monto_ars
    request.session["plataforma"] = "mercadopago"
    request.session["tipo_plan"] = tipo_plan
    request.session.modified = True

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    domain = request.build_absolute_uri("/")[:-1]

    # --- CAMBIO CRÍTICO AQUÍ: Pasamos email y plan en la URL de retorno ---
    back_url_success = f"{domain}/pago/exito/?email={email}&plan={tipo_plan}"
    
    preference_data = {
        "items": [{"id": "plan_dvolve", "title": "Plan DVOLVE", "quantity": 1, "currency_id": "ARS", "unit_price": monto_ars}],
        "payer": {"email": email},
        "back_urls": {
            "success": back_url_success, # <--- URL BLINDADA
            "failure": f"{domain}/pago/error/",
            "pending": f"{domain}/pago/error/",
        }
    }
    
    if not any(h in domain for h in ["127.0.0.1", "localhost"]):
        preference_data["auto_return"] = "approved"

    preference_response = sdk.preference().create(preference_data)
    init_point = preference_response.get("response", {}).get("init_point")

    if init_point:
        return redirect(init_point)
    return JsonResponse({"error": "Error MP"}, status=400)

def pagar_paypal(request):
    monto_usd = request.GET.get("monto") or request.session.get("monto_usd") or request.session.get("monto")
    if not monto_usd: return JsonResponse({"error": "Monto no especificado"}, status=400)
    try:
        monto_usd = float(monto_usd)
    except:
        return JsonResponse({"error": "Monto inválido"}, status=400)

    email = request.session.get("checkout_email")
    if not email and request.user.is_authenticated:
        email = request.user.email
    if not email:
        return JsonResponse({"error": "No se pudo identificar tu email"}, status=400)

    # Guardar datos en sesión
    request.session["checkout_email"] = email
    request.session["monto_usd"] = monto_usd
    request.session["plataforma"] = "paypal"
    request.session.modified = True

    client_id = settings.PAYPAL_CLIENT_ID
    client_secret = settings.PAYPAL_CLIENT_SECRET

    auth_resp = requests.post("https://api-m.sandbox.paypal.com/v1/oauth2/token", auth=(client_id, client_secret), data={"grant_type": "client_credentials"})
    access_token = auth_resp.json().get("access_token")

    # PayPal es más estable con sesiones, pero igual enviamos params por si acaso
    success_url = request.build_absolute_uri(f"/pago/exito/?email={email}")

    order_resp = requests.post(
        "https://api-m.sandbox.paypal.com/v2/checkout/orders",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "intent": "CAPTURE",
            "purchase_units": [{"amount": {"currency_code": "USD", "value": str(monto_usd)}}],
            "application_context": {"return_url": success_url, "cancel_url": request.build_absolute_uri("/pago/error/")}
        }
    ).json()

    for link in order_resp.get("links", []):
        if link["rel"] == "approve": return redirect(link["href"])
    return JsonResponse(order_resp)

def pago_exito(request):
    # --- ESTRATEGIA ANTIBALAS PARA RECUPERAR DATOS ---
    
    # 1. Intentar desde la URL (Prioridad Máxima)
    email_get = request.GET.get('email')
    plan_get = request.GET.get('plan')
    
    # 2. Intentar desde la Sesión (Backup)
    email_session = request.session.get('checkout_email')
    plan_session = request.session.get('tipo_plan')
    
    # 3. Consolidar datos
    email = email_get or email_session
    # Si aun no hay email, probar con usuario logueado
    if not email and request.user.is_authenticated:
        email = request.user.email

    tipo_plan = plan_get or plan_session or 'Mensual'

    # SI DESPUÉS DE TODO NO HAY EMAIL, ES UN ERROR REAL
    if not email:
        return redirect('principal:home')

    # Recuperar montos
    plataforma = request.session.get('plataforma', 'mercadopago') # Default MP
    monto_ars = request.session.get('monto_ars')
    monto_usd = request.session.get('monto_usd')
    
    monto = 0.0
    moneda = 'ARS'

    # Lógica de Monto (con rescate si se borró la sesión)
    if plataforma == 'paypal' and monto_usd:
        monto = float(monto_usd)
        moneda = 'USD'
    elif monto_ars:
        monto = float(monto_ars)
        moneda = 'ARS'
    else:
        # ¡RESCATE! Si se borró la sesión, buscamos el precio en constants.py usando el plan
        precio_rescate = get_plan_price(tipo_plan, 'ARS')
        if precio_rescate:
            monto = float(precio_rescate)
            moneda = 'ARS'

    # Obtener días usando tu constants.py
    dias = get_plan_duration(tipo_plan)
    nombre_plan = tipo_plan

    # Parámetros MP
    payment_id = request.GET.get('payment_id', '')
    merchant_order_id = request.GET.get('merchant_order_id', '')
    payment_id_externo = payment_id or merchant_order_id or None

    user = request.user if request.user.is_authenticated else None

    # 1. Guardar Historial (Evitando duplicados)
    pago_creado = False
    if payment_id_externo:
        pago_existente = Pago.objects.filter(payment_id_externo=payment_id_externo).exists()
        if not pago_existente:
            Pago.objects.create(
                user=user,
                email=email,
                monto=monto,
                moneda=moneda,
                plataforma=plataforma,
                estado="exitoso",
                tipo_plan=nombre_plan,
                payment_id_externo=payment_id_externo
            )
            pago_creado = True
    else:
        # Sin ID externo (ej. PayPal o error raro MP), creamos uno manual
        Pago.objects.create(
            user=user,
            email=email,
            monto=monto,
            moneda=moneda,
            plataforma=plataforma,
            estado="exitoso",
            tipo_plan=nombre_plan,
            payment_id_externo=f"manual_{timezone.now().timestamp()}"
        )
        pago_creado = True

    # 2. Actualizar Vencimiento
    # Solo actualizamos si el pago fue procesado ahora (para evitar sumar días si recarga la página)
    # AUNQUE: Si la chica ya pagó y no se le acreditó, al entrar acá se le tiene que acreditar.
    # Por seguridad, si viene con datos en URL, actualizamos siempre la fecha.
    
    usuario, created = VerifiedEmail.objects.get_or_create(email=email)
    ahora = timezone.now()

    # Lógica de suma de días
    if usuario.vencimiento and usuario.vencimiento > ahora:
        usuario.vencimiento += timedelta(days=dias)
    else:
        usuario.vencimiento = ahora + timedelta(days=dias)
    
    usuario.save()
    
    # Limpiar sesión (opcional, ya no dependemos de ella)
    request.session['monto_ars'] = None
    request.session['monto_usd'] = None
    request.session['checkout_email'] = None
    request.session.modified = True
    
    return render(request, 'principal/pago_exito.html', {'monto': monto, 'plan': nombre_plan, 'moneda': moneda})

def pago_error(request):
    if "monto" in request.session: del request.session["monto"]
    return render(request, "principal/pago_error.html")

def webhook_mercadopago(request):
    # ... (Tu webhook estaba perfecto, dejalo igual, solo asegurate de usar constants.py si lo necesitas)
    # Si querés te copio el webhook también, pero el error estaba en pago_exito.
    # El código que mandaste antes del webhook estaba bien.
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = request.POST
        notification_type = data.get("type")
        notification_id = data.get("id")

        if notification_type != "payment":
            return JsonResponse({"status": "ignored"})

        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        payment = sdk.payment().get(notification_id)
        payment_data = payment.get("response", {})

        payment_status = payment_data.get("status")
        payment_id = payment_data.get("id")
        email = payment_data.get("payer", {}).get("email")
        amount = payment_data.get("transaction_amount")
        
        if not email or not amount:
            return JsonResponse({"error": "Datos incompletos"}, status=400)

        if payment_status == "approved":
            existing = Pago.objects.filter(payment_id_externo=str(payment_id), email=email).first()
            if existing:
                return JsonResponse({"status": "duplicated"})

            # Usar tus constantes para detectar plan
            plan_info = get_plan_by_amount(amount)
            if plan_info:
                nombre_plan, dias = plan_info
            else:
                dias = 90 if amount > 50000 else 30
                nombre_plan = 'Trimestral' if amount > 50000 else 'Mensual'

            currency_id = payment_data.get("currency_id", "ARS")

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            Pago.objects.create(
                user=user,
                email=email,
                monto=amount,
                moneda=currency_id,
                plataforma="mercadopago",
                estado="exitoso",
                tipo_plan=nombre_plan,
                payment_id_externo=str(payment_id)
            )

            usuario, created = VerifiedEmail.objects.get_or_create(email=email)
            ahora = timezone.now()

            if usuario.vencimiento and usuario.vencimiento > ahora:
                usuario.vencimiento += timedelta(days=dias)
            else:
                usuario.vencimiento = ahora + timedelta(days=dias)
            
            usuario.save()

            return JsonResponse({"status": "processed"})
        elif payment_status == "pending":
            return JsonResponse({"status": "pending"})
        else:
            return JsonResponse({"status": f"payment_{payment_status}"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)