from django.urls import path
from . import views

app_name = 'email_verification'

urlpatterns = [
    path('', views.request_code_view, name='request'),
    path('check/', views.verify_code_view, name='verify'),
    path('resend/', views.resend_code_view, name='resend'),
]
