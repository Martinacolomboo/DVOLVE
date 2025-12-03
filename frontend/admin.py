from django.contrib import admin
from .models import Questionario,Video,Receta,Recomendacion,Plan,PlanArchivo

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


class PlanArchivoInline(admin.TabularInline):
    model = PlanArchivo
    extra = 1
    fields = ("archivo", "nombre", "descripcion", "orden")
    ordering = ("orden",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "destacado", "creado_en")
    search_fields = ("titulo", "descripcion")
    list_filter = ("destacado",)
    inlines = [PlanArchivoInline]

    # 🔒 para que NUNCA aparezca el slug en admin
    exclude = ("slug",)


@admin.register(PlanArchivo)
class PlanArchivoAdmin(admin.ModelAdmin):
    list_display = ("id", "plan", "nombre", "orden", "subido_en")
    list_filter = ("plan",)
    search_fields = ("nombre", "descripcion")
    ordering = ("plan", "orden")