from django.contrib import messages
from django.shortcuts import redirect, render
from urllib.parse import quote_plus

class CheckoutService:
    @classmethod
    def chequear_email_verificado(cls, request):
        if not request.session.get('checkout_email'):
            messages.warning(request, 'Primero verificá tu email.')
            return redirect('email_verification:request')
        return render(request, 'principal/metodos_pago.html')
