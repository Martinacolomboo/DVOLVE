from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'principal/home.html')
def segunda_pagina(request):
    return render(request, 'principal/segunda_pagina.html')
def pagos(request):
    return render(request, 'principal/pagos.html')
def privacidad(request):
    return render(request, "principal/privacidad.html")
