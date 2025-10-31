from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'principal'
urlpatterns = [
    path('', views.home, name="principal"), # Esta ruta es la que se usará para la página de inicio
    path('home/', views.home, name='home'),
    path('plan/', views.segunda_pagina, name='segunda_pagina'), # Esta ruta es para la segunda página
    path('pagos/', views.pagos, name='pagos'),
    path("privacidad/", views.privacidad, name="privacidad"),
    path('checkout/', views.metodos_pago, name='metodos_pago'),
    path('pago/mercadopago/', views.pagar_mercadopago, name='pagar_mercadopago'),
    path('pago/paypal/', views.pagar_paypal, name='pagar_paypal'),
    path('pago/exito/', views.pago_exito, name='pago_exito'),
    path('pago/error/', views.pago_error, name='pago_error'),
    path('segunda_pagina/', views.segunda_pagina, name='segunda_pagina'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)