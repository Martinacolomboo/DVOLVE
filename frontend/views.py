from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Questionario,Video,Receta,Recomendacion
from django.contrib.admin.views.decorators import staff_member_required

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None: 
            login(request, user)
            if user.is_superuser:
                return redirect("frontend:panel_admin")  # 🚀 admin
            else:
                return redirect("frontend:dashboard")     

        return render(request, "frontend/login.html", {
            "error": "Usuario no encontrado. Si no tenés cuenta, registrate."
        })

    return render(request, "frontend/login.html")

@staff_member_required
def panel_admin(request):
    return render(request, "frontend/panel_admin.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            return render(request, "frontend/register.html", {
                "error": "Ese usuario ya existe. Iniciá sesión."
            })
        # Crear usuario normal (cliente)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = False   # aseguramos que NO sea admin
        user.save()

        login(request, user)
        return redirect("frontend:bienvenida")  # 👈 flujo de clientes

    return render(request, "frontend/register.html")

@login_required
def home(request):
    return render(request, "frontend/index.html")



@login_required
def community_view(request):
    return render(request, "frontend/community.html")

@login_required
def live_view(request):
    return render(request, "frontend/live.html")

@login_required
def podcast_view(request):
    return render(request, "frontend/podcast.html")


@login_required
def cuestionario_entrenamiento_view(request):
    if request.method == "POST":
        required_fields = [
            "health_conditions", "weight", "age", "height",
            "training_goal", "training_level",
            "other_activity", "training_days", "sleep"
        ]

        missing = [f for f in required_fields if not request.POST.get(f)]
        if missing:
            return render(request, "frontend/cuestionario_entrenamiento.html", {
                "error": "Todos los campos son obligatorios."
            })

        Questionario.objects.update_or_create(
            user=request.user,
            defaults={
                "health_conditions": request.POST.get("health_conditions"),
                "weight": request.POST.get("weight"),
                "age": request.POST.get("age"),
                "height": request.POST.get("height"),
                "training_goal": request.POST.get("training_goal"),
                "training_level": request.POST.get("training_level"),
                "other_activity": request.POST.get("other_activity"),
                "training_days": request.POST.get("training_days"),
                "sleep": request.POST.get("sleep"),
            }
        )
        return redirect("frontend:cuestionario_alimentacion")
    return render(request, "frontend/cuestionario_entrenamiento.html")

@login_required
def cuestionario_alimentacion_view(request):
    if request.method == "POST":
        required_fields = [
            "current_diet", "diet_restrictions", "thyroid",
            "meals", "snacks", "meal_schedule", "hydration"
        ]

        missing = [f for f in required_fields if not request.POST.get(f)]
        if missing:
            return render(request, "frontend/cuestionario_alimentacion.html", {
                "error": "Todos los campos son obligatorios.",
                "data": request.POST 
            })

        Questionario.objects.update_or_create(
            user=request.user,
            defaults={
                "current_diet": request.POST.get("current_diet"),
                "diet_restrictions": request.POST.get("diet_restrictions"),
                "thyroid": request.POST.get("thyroid"),
                "meals": request.POST.get("meals"),
                "snacks": request.POST.get("snacks"),
                "meal_schedule": request.POST.get("meal_schedule"),
                "hydration": request.POST.get("hydration"),
            }
        )
        return redirect("frontend:dashboard")
    return render(request, "frontend/cuestionario_alimentacion.html")
@login_required
def dashboard_view(request):
    cuestionario = None
    videos = []
    recetas = []

    try:
        cuestionario = Questionario.objects.get(user=request.user)
        videos = Video.objects.filter(objetivo=cuestionario.training_goal)
        recetas = Receta.objects.filter(objetivo=cuestionario.training_goal)
    except Questionario.DoesNotExist:
        pass  # si no hay cuestionario, no mostramos nada

    return render(request, "frontend/dashboard.html", {
        "videos": videos,
        "recetas": recetas,
        "cuestionario": cuestionario,
    })


@login_required
def videos_view(request):
    cuestionario = Questionario.objects.filter(user=request.user).first()

    # Recomendados en base al objetivo y nivel
    recomendados = []
    if cuestionario:
        recomendados = Video.objects.filter(
            objetivo=cuestionario.training_goal,
            nivel=cuestionario.training_level
        )[:3]

    videos = Video.objects.all().order_by("-creado_en")

    return render(request, "frontend/video.html", {
        "videos": videos,
        "recomendados": recomendados,
    })

@login_required
def recetas_view(request):
    recetas = Receta.objects.all().order_by("-creado_en")
    return render(request, "frontend/recetas.html", {"recetas": recetas})

@login_required
def bienvenida_view(request):
    return render(request, "frontend/bienvenida.html")
from django.contrib import messages
from django.contrib import messages

@staff_member_required
def gestion_videos(request):
    if not request.user.is_superuser:
        return redirect("frontend:dashboard")

    video_edit = None
    video_id = request.GET.get("edit")
    if video_id:
        video_edit = Video.objects.filter(id=video_id).first()

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        objetivo = request.POST.get("objetivo", "").strip()
        nivel = request.POST.get("nivel", "").strip()
        entorno = request.POST.get("entorno", "").strip()
        apto_para = request.POST.get("apto_para", "").strip()
        requiere_equipo = bool(request.POST.get("requiere_equipo"))
        portada = request.FILES.get("portada")
        archivo = request.FILES.get("archivo")

        # 🧩 Nueva validación (detecta campos vacíos y espacios)
        campos_obligatorios = {
            "Título": titulo,
            "Objetivo": objetivo,
            "Nivel": nivel,
            "Entorno": entorno,
            "Apto para": apto_para,
        }
        vacios = [nombre for nombre, valor in campos_obligatorios.items() if not valor]

        if vacios:
            messages.error(request, f"Por favor completá los siguientes campos obligatorios: {', '.join(vacios)}.")
            return render(request, "frontend/gestion_videos.html", {
                "videos": Video.objects.all().order_by("-creado_en"),
                "video_edit": video_edit
            })

        # ✅ EDITAR VIDEO EXISTENTE
        if video_edit:
            video_edit.titulo = titulo
            video_edit.descripcion = descripcion
            video_edit.objetivo = objetivo
            video_edit.nivel = nivel
            video_edit.entorno = entorno
            video_edit.apto_para = apto_para
            video_edit.requiere_equipo = requiere_equipo

            if archivo:
                video_edit.archivo = archivo
            elif not video_edit.archivo:
                messages.error(request, "Debe haber un archivo de video cargado.")
                return render(request, "frontend/gestion_videos.html", {
                    "videos": Video.objects.all().order_by("-creado_en"),
                    "video_edit": video_edit
                })

            if portada:
                video_edit.thumbnail = portada

            video_edit.save()
            messages.success(request, "✅ Video actualizado correctamente.")
            return redirect("frontend:gestion_videos")

        # ✅ CREAR NUEVO VIDEO
        else:
            if not archivo:
                messages.error(request, "Debés subir un archivo de video.")
                return render(request, "frontend/gestion_videos.html", {
                    "videos": Video.objects.all().order_by("-creado_en"),
                    "video_edit": None
                })

            Video.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                objetivo=objetivo,
                nivel=nivel,
                entorno=entorno,
                apto_para=apto_para,
                requiere_equipo=requiere_equipo,
                creado_por=request.user,
                archivo=archivo,
                thumbnail=portada
            )
            messages.success(request, "✅ Video subido correctamente.")
            return redirect("frontend:gestion_videos")

    videos = Video.objects.all().order_by("-creado_en")
    return render(request, "frontend/gestion_videos.html", {
        "videos": videos,
        "video_edit": video_edit
    })

@staff_member_required
def eliminar_video(request, video_id):
    video = Video.objects.get(id=video_id)
    video.delete()
    return redirect("frontend:gestion_videos")
    
@staff_member_required
def gestion_recetas(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        archivo = request.FILES.get("archivo")
        objetivo = request.POST.get("objetivo")

        Receta.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            archivo=archivo,
            objetivo=objetivo
        )
        return redirect("frontend:gestion_recetas")

    recetas = Receta.objects.all().order_by("-creado_en")
    return render(request, "frontend/gestion_recetas.html", {"recetas": recetas})