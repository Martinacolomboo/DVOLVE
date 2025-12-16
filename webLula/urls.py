"""
URL configuration for webLula project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from frontend.sitemaps import StaticViewSitemap
from django.contrib.sitemaps.views import sitemap
sitemaps = {
    'static': StaticViewSitemap,
    # Puedes agregar más sitemaps aquí
}
urlpatterns = [
    path(
            "googled64f2cdb0ed07b77.html",
            TemplateView.as_view(template_name="googled64f2cdb0ed07b77.html"),
        ),
    path('admin/', admin.site.urls),
    path('', include(('principal.urls', 'principal'), namespace='principal')),
    path('verify-email/', include(('email_verification.urls', 'email_verification'), namespace='email_verification')),
    path("clientes/", include("clientes.urls")),
    path("frontend/", include(('frontend.urls', 'frontend'), namespace='frontend')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)