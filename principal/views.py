from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'principal/index.html')
def segunda_pagina(request):
    return render(request, 'principal/segunda_pagina.html')