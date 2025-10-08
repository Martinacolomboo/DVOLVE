from urllib import request
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, render
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from urllib.parse import quote_plus
from django.contrib import messages
from django.shortcuts import render, redirect
from .helpers import CheckoutService
import mercadopago
from django.http import JsonResponse
from django.http import HttpResponse
def home(request):
    return render(request, 'principal/home.html')
def segunda_pagina(request):
    return render(request, 'principal/segunda_pagina.html')
def pagos(request):
    return render(request, 'principal/pagos.html')
def privacidad(request):
    return render(request, "principal/privacidad.html")
def metodos_pago(request):
    response = CheckoutService.chequear_email_verificado(request)
    if response is not None:
        return response

    
    # Si el email está verificado y hay que mostrar los métodos de pago:
    monto = request.GET.get("monto") or request.session.get("monto")
    print("🟩 (metodos_pago) monto en sesión:", monto)
    if not monto:
        monto = request.session.get("monto")
        print("🟩 monto desde sesión:", monto)
    else:
        # Guardamos en sesión para los pasos siguientes
        request.session["monto"] = monto
        request.session.modified = True
    if not monto:
        print("⚠️ No hay monto, redirigiendo a /pagos/")
        return redirect("principal:pagos")

    return render(request, "principal/metodos_pago.html", {"monto": monto})
import requests
def pagar_mercadopago(request):
    monto = request.GET.get("monto") or request.session.get("monto")
    print("💰 [MercadoPago] Monto recibido:", monto)

    # 2️⃣ Validar monto
    try:
        monto = float(monto)
        if monto <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"error": f"Monto inválido o no especificado: {monto}"}, status=400)

    sdk = mercadopago.SDK("APP_USR-4007951274971270-100619-4c629452bb54b3574510afa870fde8f9-2909305533")
    domain = request.build_absolute_uri("/")[:-1]
    print("🟢 Dominio construido:", domain)

    preference_data = {
        "items": [
            {
                "id": "plan_dvolve",
                "title": "Plan DVOLVE",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(monto)
            }
        ],
        "payer": {
            "email": request.session.get("email_verified_address", "test_user@test.com")
        },
        "back_urls": {
            "success": f"{domain}/pago/exito/",
            "failure": f"{domain}/pago/error/",
            "pending": f"{domain}/pago/error/",
        }
    }

    # ✅ Solo agregar auto_return si NO estás en localhost
    if not any(host in domain for host in ["127.0.0.1", "localhost"]):
        preference_data["auto_return"] = "approved"
    else:
        print("🚫 Ambiente local detectado, se omite auto_return")

    # 🔧 Limpieza extra (por si el SDK lo agrega igual)
    if "127.0.0.1" in domain or "localhost" in domain:
        if "auto_return" in preference_data:
            del preference_data["auto_return"]
            print("🧹 auto_return eliminado del payload (entorno local detectado)")

    import json
    print("📦 Payload FINAL enviado:", json.dumps(preference_data, indent=2))

    preference_response = sdk.preference().create(preference_data)
    print("🔍 Respuesta completa:", preference_response)

    response_data = preference_response.get("response", {})
    init_point = response_data.get("init_point")

    if not init_point:
        return JsonResponse({
            "error": "Mercado Pago no devolvió init_point",
            "detalle": response_data
        }, status=400)

    return redirect(init_point)

import requests

def pagar_paypal(request):
    # 🔹 Igual que antes, obtenemos el monto
    monto = request.GET.get("monto") or request.session.get("monto")
    if not monto:
        return JsonResponse({"error": "Monto no especificado."}, status=400)

    monto = float(monto)

    client_id = "TU_CLIENT_ID_PAYPAL"
    client_secret = "TU_CLIENT_SECRET_PAYPAL"

    
    # Obtener token de acceso de PayPal
    auth_response = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    ).json()

    access_token = auth_response["access_token"]

    # Crear orden de pago
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {"amount": {"currency_code": "USD", "value": str(monto)}}
        ],
        "application_context": {
            "return_url": request.build_absolute_uri("/pago/exito/"),
            "cancel_url": request.build_absolute_uri("/pago/error/")
        }
    }

    order_response = requests.post(
        "https://api-m.sandbox.paypal.com/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json=order_data,
    ).json()

    # Redirigir al link de aprobación
    for link in order_response["links"]:
        if link["rel"] == "approve":
            return redirect(link["href"])

    return JsonResponse(order_response)
from django.http import HttpResponse

def pago_exito(request):
    monto = request.session.get("monto")
    return render(request, "principal/pago_exito.html", {"monto": monto})

def pago_error(request):
    return render(request, "principal/pago_error.html")