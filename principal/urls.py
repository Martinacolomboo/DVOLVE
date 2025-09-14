from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"), # Esta ruta es la que se usará para la página de inicio
    path('plan/', views.segunda_pagina, name='segunda_pagina'), # Esta ruta es para la segunda página
    path('pagos/', views.pagos, name='pagos'),
    path("privacidad/", views.privacidad, name="privacidad")

]