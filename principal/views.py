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

def home(request):
    return render(request, 'principal/home.html')
def segunda_pagina(request):
    return render(request, 'principal/segunda_pagina.html')
def pagos(request):
    return render(request, 'principal/pagos.html')
def privacidad(request):
    return render(request, "principal/privacidad.html")
def metodos_pago(request):
    return CheckoutService.chequear_email_verificado(request)
