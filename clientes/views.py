from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def index(request):
    return render(request, "clientes/index.html")

def formulario(request):
    return render(request, "clientes/formulario.html")

def plan(request):
    return render(request, "clientes/plan.html")
def login_view(request):
    if request.method == "POST": 
        username = request.POST.get("username") 
        password = request.POST.get("password") 
        user = authenticate(request, username=username, password=password) 
        if user is not None: 
            login(request, user) 
            return redirect("clientes:index") # redirige a la zona de clientes
        else: messages.error(request, "Usuario o contraseña incorrectos") 
    return render(request, "clientes/login.html")
def logout_view(request):
    logout(request)
    return redirect("clientes:login")