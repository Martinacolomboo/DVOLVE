from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'principal/home.html')
def segunda_pagina(request):
    return render(request, 'principal/segunda_pagina.html')