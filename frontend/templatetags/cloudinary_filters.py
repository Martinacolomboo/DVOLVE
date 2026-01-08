# frontend/templatetags/cloudinary_filters.py

from django import template

register = template.Library()

@register.filter
def optimize_url(url, width=300):
    """
    Toma una URL de Cloudinary y le inserta transformaciones para optimizarla.
    Uso: {{ imagen.url|optimize_url:400 }}
    """
    if not url or 'cloudinary.com' not in url:
        return url

    # Dividimos la URL para insertar la transformación después de "/upload/"
    parts = url.split('/upload/')
    if len(parts) != 2:
        return url

    # Definimos la transformación: ancho variable, corte fill, gravedad automática, calidad y formato auto
    transformation = f'w_{width},c_fill,g_auto,q_auto,f_auto/'
    
    # Reconstruimos la URL
    optimized_url = parts[0] + '/upload/' + transformation + parts[1]
    
    return optimized_url