from django.urls import path
from . import views

app_name = "clientes"

urlpatterns = [
    path("", views.index, name="index"),  # página principal de clientes
    path("formulario/", views.formulario, name="formulario"),  # cuestionario o form
    path("plan/", views.plan, name="plan"),  # página privada del plan
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
