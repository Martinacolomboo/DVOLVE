from django.urls import path
from . import views

app_name = "frontend"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("registro/", views.register_view, name="registro"),
    path("home/", views.home, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("community/", views.community_view, name="community"),
    path("live/", views.live_view, name="live"),
    path("podcast/", views.podcast_view, name="podcast"),
    path("cuestionario/entrenamiento/", views.cuestionario_entrenamiento_view, name="cuestionario_entrenamiento"),
    path("videos/", views.videos_view, name="video"),
    path("recetas/", views.recetas_view, name="recetas"),
    path("bienvenida/", views.bienvenida_view, name="bienvenida"),
    path("cuestionario/alimentacion/", views.cuestionario_alimentacion_view, name="cuestionario_alimentacion"),
    path("panel-admin/", views.panel_admin, name="panel_admin"),
    path("panel-admin/", views.panel_admin, name="panel_admin"),
    path("admin/videos/", views.gestion_videos, name="gestion_videos"),
    path("admin/recetas/", views.gestion_recetas, name="gestion_recetas"),
    path("admin/videos/eliminar/<int:video_id>/", views.eliminar_video, name="eliminar_video"),
    path('admin/recetas/editar/<int:receta_id>/', views.gestion_recetas_edit, name='editar_receta'),
    path('admin/recetas/eliminar/<int:receta_id>/', views.gestion_recetas_delete, name='eliminar_receta'),


]
