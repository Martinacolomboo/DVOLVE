from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import mercadopago
import requests

from .models import Pago, VerifiedEmail
from .helpers import CheckoutService

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
    monto = request.GET.get("monto") or request.session.get("monto")
    try:
        monto = float(monto)
    except:
        return JsonResponse({"error": "Monto inválido"}, status=400)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    domain = request.build_absolute_uri("/")[:-1]
    
    preference_data = {
        "items": [{"id": "plan_dvolve", "title": "Plan DVOLVE", "quantity": 1, "currency_id": "ARS", "unit_price": monto}],
        "payer": {"email": request.session.get("email_verified_address", "test@test.com")},
        "back_urls": {
            "success": f"{domain}/pago/exito/",
            "failure": f"{domain}/pago/error/",
            "pending": f"{domain}/pago/error/",
        }
    }
    if not any(h in domain for h in ["127.0.0.1", "localhost"]):
        preference_data["auto_return"] = "approved"

    preference_response = sdk.preference().create(preference_data)
    init_point = preference_response.get("response", {}).get("init_point")

    if init_point: return redirect(init_point)
    return JsonResponse({"error": "Error MP"}, status=400)

def pagar_paypal(request):
    monto = request.GET.get("monto") or request.session.get("monto")
    if not monto: return JsonResponse({"error": "Monto no especificado"}, status=400)
    monto = float(monto)

    client_id = settings.PAYPAL_CLIENT_ID
    client_secret = settings.PAYPAL_CLIENT_SECRET

    auth_resp = requests.post("https://api-m.sandbox.paypal.com/v1/oauth2/token", auth=(client_id, client_secret), data={"grant_type": "client_credentials"})
    access_token = auth_resp.json().get("access_token")

    order_resp = requests.post(
        "https://api-m.sandbox.paypal.com/v2/checkout/orders",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "intent": "CAPTURE",
            "purchase_units": [{"amount": {"currency_code": "USD", "value": str(monto)}}],
            "application_context": {"return_url": request.build_absolute_uri("/pago/exito/"), "cancel_url": request.build_absolute_uri("/pago/error/")}
        }
    ).json()

    for link in order_resp.get("links", []):
        if link["rel"] == "approve": return redirect(link["href"])
    return JsonResponse(order_resp)

def pago_exito(request):
    monto = request.session.get('monto')
    email = request.session.get('checkout_email')
    
    if not monto or not email:
        return redirect('principal:home')

    # Detectar Plan y Días
    es_trimestral = float(monto) > 50000
    dias = 90 if es_trimestral else 30
    nombre_plan = 'Trimestral' if es_trimestral else 'Mensual'

    # 1. Guardar Historial
    Pago.objects.create(email=email, monto=monto, tipo_plan=nombre_plan, estado="exitoso")

    # 2. Actualizar Vencimiento en la tabla de SUSCRIPCIONES
    usuario, created = VerifiedEmail.objects.get_or_create(email=email)
    ahora = timezone.now()

    if usuario.vencimiento and usuario.vencimiento > ahora:
        usuario.vencimiento += timedelta(days=dias)
    else:
        usuario.vencimiento = ahora + timedelta(days=dias)
    
    usuario.save()
    request.session['monto'] = None
    
    return render(request, 'principal/pago_exito.html', {'monto': monto, 'plan': nombre_plan})

def pago_error(request):
    if "monto" in request.session: del request.session["monto"]
    return render(request, "principal/pago_error.html")