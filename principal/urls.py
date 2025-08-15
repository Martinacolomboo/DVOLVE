from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Esta ruta es la que se usará para la página de inicio
]