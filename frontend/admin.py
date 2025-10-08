from django.contrib import admin
from .models import Questionario,Video,Receta,Recomendacion

admin.site.register(Questionario)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "creado_por", "creado_en")
    search_fields = ("titulo",)

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "creado_en", "objetivo", "destacado")
    list_editable = ("destacado",)
    search_fields = ("titulo",)

@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "creado_en","destacado")
    search_fields = ("titulo", "contenido")
    list_editable = ("destacado",)