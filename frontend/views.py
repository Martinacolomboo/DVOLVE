from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Questionario,Video,Receta,Recomendacion
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from email_verification.models import EmailVerification as VerifiedEmail
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            email = (user.email or "").lower()

            # ✅ Verificamos si tiene correo y si está verificado
            if not email:
                messages.error(request, "Tu cuenta no tiene un correo asociado.")
            elif not VerifiedEmail.objects.filter(email=email).exists():
                messages.error(
                    request,
                    "Tu correo no está verificado. Revisá tu email o verificá tu cuenta antes de ingresar."
                )
                # Podés guardar el mail en sesión para facilitar la verificación
                request.session["ev_email"] = email
                # 👉 opcional: redirigir al flujo de verificación
                # return redirect("email_verification:request")
            else:
                # ✅ Email verificado → permitir acceso
                login(request, user)
                if user.is_superuser:
                    return redirect("frontend:panel_admin")
                else:
                    return redirect("frontend:dashboard")

        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "frontend/login.html")

@staff_member_required
def panel_admin(request):
    return render(request, "frontend/panel_admin.html")

def register_view(request):
    email_verified = request.session.get("email_verified_address")

    if not email_verified:
        messages.error(request, "Primero verificá tu correo antes de registrarte.")
        return redirect("email_verification:request")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # 2️⃣ Comprobamos si el usuario ya existe
        if User.objects.filter(username=username).exists():
            return render(request, "frontend/register.html", {
                "error": "Ese usuario ya existe. Iniciá sesión."
            })

        # 3️⃣ Creamos usuario con el mail verificado
        user = User.objects.create_user(
            username=username,
            email=email_verified,
            password=password
        )
        user.is_staff = False
        user.save()

        login(request, user)
        return redirect("frontend:bienvenida")

    # 4️⃣ Mostramos el email verificado en el formulario (solo lectura)
    return render(request, "frontend/register.html", {
        "verified_email": email_verified
    })
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
    recetas_filtradas = Receta.objects.all()  # por defecto, todas las recetas

    try:
        cuestionario = Questionario.objects.get(user=request.user)
    except Questionario.DoesNotExist:
        messages.warning(
            request, 
            "Completá tu cuestionario de alimentación para obtener recetas personalizadas."
        )
        # Si no hay cuestionario, usamos todas las recetas sin filtrar
        user_restrictions = "ninguna"
        user_thyroid = "ninguna"
    else:
        # Si hay cuestionario, aplicamos filtros
        user_restrictions = cuestionario.diet_restrictions
        user_thyroid = cuestionario.thyroid

        # Filtro por objetivo (si lo querés usar)
        q_filters = Q(objetivo=cuestionario.training_goal) | Q(objetivo=cuestionario.diet_goal)

        # Filtro por restricciones alimentarias
        restricciones_q = Q(diet_restrictions="ninguna") | Q(diet_restrictions=user_restrictions)

        # Filtro por tiroides
        thyroid_q = Q(thyroid="ninguna") | Q(thyroid=user_thyroid)

        # Aplicar filtros combinados
        recetas_filtradas = Receta.objects.filter(
            q_filters & restricciones_q & thyroid_q
        ).order_by('-destacado', '-creado_en')

    context = {
        'recetas': recetas_filtradas,
        'user_restrictions': user_restrictions,
        'user_thyroid': user_thyroid,
    }
    return render(request, 'frontend/recetas.html', context)

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
    if not request.user.is_superuser:
        return redirect('frontend:dashboard')

    if request.method == 'POST':
        # Lógica para CREAR una nueva receta
        try:
            # Leer campos del formulario
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            objetivo = request.POST.get('objetivo')
            categoria_comida = request.POST.get('categoria_comida', 'almuerzo')
            diet_restrictions = request.POST.get('diet_restrictions', 'ninguna')
            thyroid = request.POST.get('thyroid', 'ninguna')
            destacado = request.POST.get('destacado') == 'on'

            # Campos numéricos: convertir a int, si viene vacío poner None
            def to_int(value):
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return None

            tiempo_prep = to_int(request.POST.get('tiempo_prep'))
            porciones = to_int(request.POST.get('porciones'))
            calorias = to_int(request.POST.get('calorias'))
            proteinas = to_int(request.POST.get('proteinas'))
            carbohidratos = to_int(request.POST.get('carbohidratos'))
            grasas = to_int(request.POST.get('grasas'))

            # Archivos
            archivo = request.FILES.get('archivo')
            imagen_portada = request.FILES.get('imagen_portada')

            # Crear la receta
            Receta.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                objetivo=objetivo,
                categoria_comida=categoria_comida,
                diet_restrictions=diet_restrictions,
                thyroid=thyroid,
                destacado=destacado,
                tiempo_prep=tiempo_prep,
                porciones=porciones,
                calorias=calorias,
                proteinas=proteinas,
                carbohidratos=carbohidratos,
                grasas=grasas,
                archivo=archivo,
                imagen_portada=imagen_portada,
            )

            messages.success(request, "Receta subida correctamente.")
        except Exception as e:
            messages.error(request, f"Error al subir la receta: {e}")
        
        return redirect('frontend:gestion_recetas')

    # Lógica GET: Mostrar el formulario de creación vacío y la lista
    recetas = Receta.objects.all().order_by('-creado_en')
    context = {
        'recetas': recetas,
        # receta_edit es None por defecto, solo muestra el formulario de creación
    }
    return render(request, 'frontend/gestion_recetas.html', context)
@login_required
def gestion_recetas_edit(request, receta_id):
    if not request.user.is_superuser:
        return redirect('frontend:dashboard')

    receta_edit = get_object_or_404(Receta, id=receta_id)

    if request.method == 'POST':
        try:
            # 1. Obtenemos el objeto existente (ya hecho por get_object_or_404)
            receta_obj = receta_edit
            
            # 2. Actualizamos todos los campos que SÍ deben cambiar
            receta_obj.titulo = request.POST.get('titulo')
            receta_obj.descripcion = request.POST.get('descripcion')
            receta_obj.objetivo = request.POST.get('objetivo')
            receta_obj.diet_restrictions = request.POST.get('diet_restrictions')
            receta_obj.thyroid = request.POST.get('thyroid')
            receta_obj.categoria_comida = request.POST.get('categoria_comida')
            # ... (otros campos de tiempo/macros, asegúrate de convertirlos a int si es necesario)
            
            # Checkbox:
            receta_obj.destacado = request.POST.get('destacado') == 'on'
            
            # 3. LÓGICA CLAVE: Solo actualizamos 'archivo' si se sube uno nuevo.
            if request.FILES.get('archivo'):
                receta_obj.archivo = request.FILES.get('archivo')
            
            # 4. También para la imagen de portada:
            if request.FILES.get('imagen_portada'):
                receta_obj.imagen_portada = request.FILES.get('imagen_portada')
                
            receta_obj.save()
            messages.success(request, "Receta actualizada correctamente.")
            return redirect('frontend:gestion_recetas') 
            
        except Exception as e:
            messages.error(request, f"Error al actualizar la receta: {e}")
            
    # Lógica GET para mostrar el formulario precargado
    recetas = Receta.objects.all().order_by('-creado_en') 
    context = {
        'recetas': recetas,
        'receta_edit': receta_edit, 
    }
    return render(request, 'frontend/gestion_recetas.html', context)

@login_required
def gestion_recetas_delete(request, receta_id):
    if not request.user.is_superuser:
        return redirect('frontend:dashboard')

    receta = get_object_or_404(Receta, id=receta_id)

    if request.method == 'POST':
        # La eliminación debe hacerse con un formulario POST
        try:
            receta.delete()
            messages.success(request, f"Receta '{receta.titulo}' eliminada.")
        except Exception as e:
            messages.error(request, f"Error al eliminar la receta: {e}")
    else:
        # Si se intenta acceder por GET (directamente por URL)
        messages.error(request, "Método de eliminación no permitido.")
        
    return redirect('frontend:gestion_recetas')