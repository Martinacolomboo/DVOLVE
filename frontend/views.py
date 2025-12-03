from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse, NoReverseMatch
from django.contrib import messages
# MODELOS PROPIOS
from .models import Questionario, Video, Receta, Recomendacion, Plan, Podcast, PlanArchivo,Biblioteca

# CORRECCIÓN CRÍTICA: Importamos el modelo de suscripción real
from principal.models import VerifiedEmail

# ==============================================================================
# 1. AUTENTICACIÓN Y REGISTRO
# ==============================================================================

def register_view(request):
    verified_email = request.session.get("email_verified_address")

    if request.method == "POST":
        # PASO 2: Finalizar registro
        if "finish_registration" in request.POST:
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()
            
            # CORRECCIÓN: 'frontend:registro'
            if not verified_email: return redirect("frontend:registro")

            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, f"El usuario '{username}' ya existe.")
                return render(request, "frontend/register.html", {"verified_email": verified_email})

            user = User.objects.create_user(username=username, email=verified_email, password=password)
            user.is_staff = False
            user.save()
            
            login(request, user)
            return redirect("frontend:bienvenida")

        # PASO 1: Ingresar Email
        else:
            email_input = request.POST.get("email", "").strip().lower()
            # CORRECCIÓN: 'frontend:registro'
            if not email_input: return redirect("frontend:registro")

            if User.objects.filter(email=email_input).exists():
                messages.error(request, "Ya tenés cuenta. Iniciá sesión.")
                return redirect("frontend:login")

            if VerifiedEmail.objects.filter(email=email_input).exists():
                request.session["email_verified_address"] = email_input
                # CORRECCIÓN: 'frontend:registro'
                return redirect("frontend:registro")
            else:
                request.session['ev_email'] = email_input
                # CORRECCIÓN IMPORTANTE: La "próxima parada" también debe ser 'frontend:registro'
                request.session['verification_next'] = 'frontend:registro'
                return redirect("email_verification:request")

    return render(request, "frontend/register.html", {"verified_email": verified_email})

def login_view(request):
    prefill = request.session.pop('prefill_email', '')
    show_pay_button = False
    pay_url = None
    error_message = None

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect("frontend:panel_admin")

            # Chequeo de vencimiento de suscripción
            try:
                verif = VerifiedEmail.objects.get(email=user.email)
                if verif.vencimiento and verif.vencimiento > timezone.now():
                    login(request, user)
                    return redirect("frontend:dashboard")
                else:
                    error_message = "Tu plan venció. Por favor renovalo."
                    show_pay_button = True
                    pay_url = reverse('principal:pagos')
            except VerifiedEmail.DoesNotExist:
                error_message = "No tenés una suscripción activa."
                show_pay_button = True
                pay_url = reverse('principal:pagos')
        else:
            error_message = "Credenciales incorrectas."

    return render(request, "frontend/login.html", {
        "prefill_email": prefill,
        "show_pay_button": show_pay_button,
        "pay_url": pay_url,
        "error_message": error_message,
    })

# ==============================================================================
# 2. VISTAS PRINCIPALES DEL CLIENTE
# ==============================================================================

@login_required
def dashboard_view(request):
    # PORTERO: Chequeo de vencimiento (Doble seguridad al entrar)
    if not (request.user.is_staff or request.user.is_superuser):
        try:
            # Buscamos la suscripción
            sub = VerifiedEmail.objects.get(email=request.user.email)
            
            # CASO 1: Nunca pagó (Vencimiento está vacío)
            if not sub.vencimiento:
                messages.info(request, "¡Bienvenida! Para acceder a los entrenamientos, primero elegí tu plan.")
                return redirect('principal:pagos')

            # CASO 2: Pagó antes, pero ya se le terminó el tiempo
            elif sub.vencimiento < timezone.now():
                messages.error(request, "Tu plan finalizó. Por favor renová tu suscripción para continuar.")
                return redirect('principal:pagos')

        except VerifiedEmail.DoesNotExist:
            # CASO 3: Error raro (No tiene registro de email verificado)
            messages.warning(request, "No encontramos una suscripción activa.")
            return redirect('principal:pagos')

    cuestionario = None
    recetas = []
    bmi_display = None
    is_overweight = False
    overweight_reason = None
    
    try:
        recommendation_url = reverse('frontend:biblioteca_view')
    except NoReverseMatch:
        recommendation_url = '/frontend/biblioteca/'

    try:
        cuestionario = Questionario.objects.get(user=request.user)
        # Nota: NO cargamos videos aquí como pediste
        recetas = Receta.objects.filter(objetivo=cuestionario.training_goal)
        
        # BMI Logic
        if cuestionario.weight and cuestionario.height:
            h_m = float(cuestionario.height) / 100.0
            bmi_val = float(cuestionario.weight) / (h_m * h_m)
            bmi_display = round(bmi_val, 1)
            
            if bmi_val >= 25: 
                is_overweight = True
                overweight_reason = "bmi"
            
            if not is_overweight and getattr(cuestionario, "peso_ideal", None):
                try:
                    peso_ideal = float(cuestionario.peso_ideal)
                    if float(cuestionario.weight) > peso_ideal * 1.10:
                        is_overweight = True
                        overweight_reason = "peso_ideal"
                except: pass

    except Questionario.DoesNotExist:
        pass

    return render(request, "frontend/dashboard.html", {
        "cuestionario": cuestionario,
        "recetas": recetas,
        "bmi": bmi_display,
        "is_overweight": is_overweight,
        "overweight_reason": overweight_reason,
        "recommendation_url": recommendation_url
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
    try:
        podcasts = Podcast.objects.all().order_by('-destacado', 'titulo')
        return render(request, 'frontend/podcast.html', {'podcasts': podcasts})
    except NameError:
        return render(request, "frontend/podcast.html")

@login_required
def bienvenida_view(request):
    return render(request, "frontend/bienvenida.html")


@login_required
def videos_view(request):
    cuestionario = Questionario.objects.filter(user=request.user).first()
    recomendados = []
    if cuestionario:
        recomendados = Video.objects.filter(
            objetivo=cuestionario.training_goal,
            nivel=cuestionario.training_level
        )[:3]
    videos = Video.objects.all().order_by("-creado_en")
    return render(request, "frontend/video.html", {"videos": videos, "recomendados": recomendados})

@login_required
def recetas_view(request):
    recetas_filtradas = Receta.objects.all().order_by('-destacado', '-creado_en')
    user_restrictions = "ninguna"
    user_thyroid = "ninguna"

    # Solo intentamos filtrar si NO es admin
    if not (request.user.is_superuser or request.user.is_staff):
        try:
            cuestionario = Questionario.objects.get(user=request.user)
            
            # Filtros personalizados
            user_restrictions = cuestionario.diet_restrictions
            user_thyroid = cuestionario.thyroid

            q_filters = Q(objetivo=cuestionario.training_goal) | Q(objetivo=cuestionario.diet_goal)
            restricciones_q = Q(diet_restrictions="ninguna") | Q(diet_restrictions=user_restrictions)
            thyroid_q = Q(thyroid="ninguna") | Q(thyroid=user_thyroid)

            recetas_filtradas = Receta.objects.filter(
                q_filters & restricciones_q & thyroid_q
            ).order_by('-destacado', '-creado_en')

        except Questionario.DoesNotExist:
            # ESTA ES LA CLAVE: Mensaje único si no hay cuestionario
            # Usamos el nivel 'info' para que sea menos alarmante que 'warning'
            messages.info(
                request, 
                "Para ver recetas personalizadas según tu objetivo, completá tu cuestionario de alimentación."
            )

    context = {
        'recetas': recetas_filtradas,
        'user_restrictions': user_restrictions,
        'user_thyroid': user_thyroid,
    }
    return render(request, 'frontend/recetas.html', context)
# ==============================================================================
# 3. CUESTIONARIOS
# ==============================================================================

@login_required
def cuestionario_entrenamiento_view(request):
    if request.method == "POST":
        required_fields = ["health_conditions", "weight", "age", "height", "training_goal", "training_level", "other_activity", "training_days", "sleep"]
        if any(not request.POST.get(f) for f in required_fields):
            return render(request, "frontend/cuestionario_entrenamiento.html", {"error": "Todos los campos son obligatorios."})

        try:
            height = float(request.POST.get("height"))
            weight = float(request.POST.get("weight"))
            base_alt = max(height, 152.4)
            peso_ideal_calc = round(45.5 + 0.9 * (base_alt - 152.4), 1)
        except:
            peso_ideal_calc = None

        defaults = {
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
        if peso_ideal_calc: defaults["peso_ideal"] = peso_ideal_calc

        Questionario.objects.update_or_create(user=request.user, defaults=defaults)
        return redirect("frontend:cuestionario_alimentacion")

    return render(request, "frontend/cuestionario_entrenamiento.html")

@login_required
def cuestionario_alimentacion_view(request):
    if request.method == "POST":
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

# ==============================================================================
# 4. GESTIÓN ADMIN (STAFF)
# ==============================================================================

@staff_member_required
def panel_admin(request):
    return render(request, "frontend/panel_admin.html")

@staff_member_required
def gestion_videos(request):
    if not request.user.is_superuser: return redirect("frontend:dashboard")
    
    video_edit = None
    if request.GET.get("edit"):
        video_edit = Video.objects.filter(id=request.GET.get("edit")).first()

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        archivo = request.FILES.get("archivo")
        # (Resto de campos simplificados para brevedad, pero mantené tu lógica de form)
        
        if video_edit:
            video_edit.titulo = titulo
            if archivo: video_edit.archivo = archivo
            # ... actualizar resto de campos ...
            video_edit.save()
            messages.success(request, "Video actualizado.")
        else:
            Video.objects.create(
                titulo=titulo,
                descripcion=request.POST.get("descripcion", ""),
                objetivo=request.POST.get("objetivo"),
                nivel=request.POST.get("nivel"),
                entorno=request.POST.get("entorno"),
                apto_para=request.POST.get("apto_para"),
                requiere_equipo=bool(request.POST.get("requiere_equipo")),
                creado_por=request.user,
                archivo=archivo,
                thumbnail=request.FILES.get("portada")
            )
            messages.success(request, "Video creado.")
        return redirect("frontend:gestion_videos")

    videos = Video.objects.all().order_by("-creado_en")
    return render(request, "frontend/gestion_videos.html", {"videos": videos, "video_edit": video_edit})

@staff_member_required
def eliminar_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.delete()
    return redirect("frontend:gestion_videos")

@staff_member_required
def gestion_recetas(request):
    if not request.user.is_superuser: 
        return redirect('frontend:dashboard')

    # 1. DETECTAR EDICIÓN
    receta_edit = None
    if request.GET.get("edit"):
        receta_edit = Receta.objects.filter(id=request.GET.get("edit")).first()

    if request.method == 'POST':
        try:
            # Datos de texto
            titulo = request.POST.get('titulo')
            descripcion = request.POST.get('descripcion')
            objetivo = request.POST.get('objetivo')
            categoria = request.POST.get('categoria_comida', 'almuerzo')
            restriccion = request.POST.get('diet_restrictions', 'ninguna')
            tiroides = request.POST.get('thyroid', 'ninguna')
            destacado = request.POST.get('destacado') == 'on'
            
            # Datos nutricionales (convertir a int o None)
            def to_int(val): return int(val) if val and val.isdigit() else None
            
            tiempo = to_int(request.POST.get('tiempo_prep'))
            porciones = to_int(request.POST.get('porciones'))
            calorias = to_int(request.POST.get('calorias'))
            proteinas = to_int(request.POST.get('proteinas'))
            carbos = to_int(request.POST.get('carbohidratos'))
            grasas = to_int(request.POST.get('grasas'))

            # Archivos
            archivo = request.FILES.get('archivo')
            portada = request.FILES.get('imagen_portada')

            # --- A) MODO EDICIÓN ---
            if receta_edit:
                receta_edit.titulo = titulo
                receta_edit.descripcion = descripcion
                receta_edit.objetivo = objetivo
                receta_edit.categoria_comida = categoria
                receta_edit.diet_restrictions = restriccion
                receta_edit.thyroid = tiroides
                receta_edit.destacado = destacado
                
                # Nutricional
                receta_edit.tiempo_prep = tiempo
                receta_edit.porciones = porciones
                receta_edit.calorias = calorias
                receta_edit.proteinas = proteinas
                receta_edit.carbohidratos = carbos
                receta_edit.grasas = grasas

                if archivo: receta_edit.archivo = archivo
                if portada: receta_edit.imagen_portada = portada
                
                receta_edit.save()
                messages.success(request, "✅ Receta actualizada correctamente.")

            # --- B) MODO CREACIÓN ---
            else:
                Receta.objects.create(
                    titulo=titulo,
                    descripcion=descripcion,
                    objetivo=objetivo,
                    categoria_comida=categoria,
                    diet_restrictions=restriccion,
                    thyroid=tiroides,
                    destacado=destacado,
                    tiempo_prep=tiempo,
                    porciones=porciones,
                    calorias=calorias,
                    proteinas=proteinas,
                    carbohidratos=carbos,
                    grasas=grasas,
                    archivo=archivo,
                    imagen_portada=portada
                )
                messages.success(request, "✅ Receta creada correctamente.")

            return redirect('frontend:gestion_recetas')

        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")

    # GET: Listar todas
    recetas = Receta.objects.all().order_by('-creado_en')
    return render(request, 'frontend/gestion_recetas.html', {
        'recetas': recetas, 
        'receta_edit': receta_edit
    })
@staff_member_required
def gestion_recetas_edit(request, receta_id):
    if not request.user.is_superuser: return redirect('frontend:dashboard')
    receta = get_object_or_404(Receta, id=receta_id)
    
    if request.method == 'POST':
        receta.titulo = request.POST.get('titulo')
        # ... actualizar resto de campos ...
        if request.FILES.get('archivo'): receta.archivo = request.FILES.get('archivo')
        receta.save()
        return redirect('frontend:gestion_recetas')

    recetas = Receta.objects.all().order_by('-creado_en')
    return render(request, 'frontend/gestion_recetas.html', {'recetas': recetas, 'receta_edit': receta})

@staff_member_required
def gestion_recetas_delete(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id)
    if request.method == 'POST':
        receta.delete()
    return redirect('frontend:gestion_recetas')

# En frontend/views.py

@staff_member_required
def gestion_planes(request):
    # Detectar edición (para que el botón editar funcione)
    plan_edit = None
    if request.GET.get("edit"):
        plan_edit = Plan.objects.filter(id=request.GET.get("edit")).first()

    if request.method == "POST":
        # 1. LEER VARIABLES DEL FORMULARIO PRIMERO
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        objetivo_leido = request.POST.get("objetivo") # <--- Leemos aquí
        destacado = request.POST.get("destacado") == "on"
        portada = request.FILES.get("portada")
        
        if plan_edit:
            # ACTUALIZAR
            plan_edit.titulo = titulo
            plan_edit.descripcion = descripcion
            plan_edit.objetivo = objetivo_leido
            plan_edit.destacado = destacado
            if portada: plan_edit.portada = portada
            plan_edit.save()
            # Guardar archivos nuevos si hay
            archivos = request.FILES.getlist("archivo")
            for f in archivos:
                PlanArchivo.objects.create(plan=plan_edit, archivo=f, nombre=f.name)
            messages.success(request, "Plan actualizado.")
        else:
            # CREAR
            new_plan = Plan.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                objetivo=objetivo_leido, # <--- Usamos la variable leída
                destacado=destacado,
                portada=portada,
                creado_por=request.user
            )
            # Guardar archivos
            archivos = request.FILES.getlist("archivo")
            for f in archivos:
                PlanArchivo.objects.create(plan=new_plan, archivo=f, nombre=f.name)
            messages.success(request, "Plan creado.")

        return redirect("frontend:gestion_planes")

    # ERROR 'meses': Quitamos 'meses' del ordenamiento
    planes = Plan.objects.all().order_by("-creado_en") 
    return render(request, "frontend/gestion_planes.html", {"planes": planes, "plan_edit": plan_edit})

from django.shortcuts import get_object_or_404 # Asegúrate de que este import exista arriba
from .models import Plan, PlanArchivo # Asegúrate de importar PlanArchivo

# --- GESTIÓN DE PLANES (CRUD Adicional) ---

@staff_member_required
def gestion_planes_edit(request, plan_id):
    plan_edit = get_object_or_404(Plan, id=plan_id)
    
    if request.method == "POST":
        # Lógica para ACTUALIZAR el plan
        
        # 1. Actualizar campos del modelo Plan (solo los textuales/checkbox)
        plan_edit.titulo = request.POST.get('titulo')
        plan_edit.descripcion = request.POST.get('descripcion')
        plan_edit.objetivo = request.POST.get('objetivo')
        plan_edit.destacado = request.POST.get('destacado') == 'on'
        
        # 2. Actualizar portada si se subió una nueva
        if request.FILES.get('portada'):
            plan_edit.portada = request.FILES.get('portada')

        plan_edit.save()

        # 3. Guardar nuevos archivos adjuntos (si se cargaron nuevos)
        archivos_subidos = request.FILES.getlist("archivo")
        if archivos_subidos:
            for f in archivos_subidos:
                PlanArchivo.objects.create(plan=plan_edit, archivo=f, nombre=f.name)
                
        messages.success(request, "✅ Plan actualizado correctamente.")
        return redirect('frontend:gestion_planes')

    # Si es GET, renderizar la lista con el plan precargado
    plans = Plan.objects.all().order_by("-destacado", "-creado_en")
    return render(request, "frontend/gestion_planes.html", {"plans": plans, "plan_edit": plan_edit})

@staff_member_required
def gestion_planes_delete(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        plan.delete()
        messages.success(request, f"Plan '{plan.titulo}' eliminado.")
    
    return redirect('frontend:gestion_planes')
# --- DETALLES DE PLANES ---

def sugerir_plan_por_cuestionario(q):
    if not q: return None
    goal = (q.training_goal or "").lower()
    if goal in ("fuerza", "hipertrofia"): return "hipertrofia"
    if goal in ("adiposidad", "perder_peso", "deficit"): return "deficit"
    return "recomposicion"

@login_required
def planes_view(request):
    planes = Plan.objects.all().order_by("-destacado", "-creado_en")
    cuestionario = Questionario.objects.filter(user=request.user).first()
    slug = sugerir_plan_por_cuestionario(cuestionario)
    recommended_plan = Plan.objects.filter(slug=slug).first() if slug else None

    return render(request, "frontend/plan_detalle.html", {
        "planes": planes,
        "recommended_plan": recommended_plan,
        "cuestionario": cuestionario,
    })

@login_required
def plan_detalle(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    return render(request, "frontend/plan_detalle.html", {"plan": plan})
# --- GESTIÓN PODCASTS (ADMIN) ---
@staff_member_required
def gestion_podcasts(request):
    if not request.user.is_superuser: return redirect("frontend:dashboard")
    
    item_edit = None
    if request.GET.get("edit"):
        item_edit = Podcast.objects.filter(id=request.GET.get("edit")).first()

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        destacado = request.POST.get("destacado") == "on"
        portada = request.FILES.get("imagen_portada")
        pdf = request.FILES.get("archivo_pdf")
        if item_edit:
            item_edit.titulo = titulo
            item_edit.descripcion = descripcion
            item_edit.destacado = destacado
            if portada: item_edit.imagen_portada = portada
            if pdf: item_edit.archivo_pdf = pdf
            
            item_edit.save()
            messages.success(request, "Podcast actualizado.")
        else:
            Podcast.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                destacado=destacado,
                imagen_portada=portada,
                archivo_pdf=pdf
            )
            messages.success(request, "Podcast creado.")
        
        return redirect("frontend:gestion_podcasts")

    items = Podcast.objects.all().order_by('-creado_en')
    return render(request, "frontend/gestion_podcast.html", {"items": items, "item_edit": item_edit})
@staff_member_required  # 1. SEGURIDAD: Solo vos (admin) podés usarla.
def gestion_podcast_delete(request, podcast_id):
    # 2. BÚSQUEDA: Busca el podcast exacto por su ID. Si no existe, da error 404.
    podcast = get_object_or_404(Podcast, id=podcast_id)
    
    # 3. ACCIÓN: Solo borra si la petición es POST (por seguridad web).
    if request.method == 'POST':
        podcast.delete()  # <--- ACÁ SE BORRA DE LA BASE DE DATOS
        messages.success(request, "Podcast eliminado correctamente.")
    
    # 4. SALIDA: Te recarga la página de gestión para que veas la lista actualizada.
    return redirect('frontend:gestion_podcast')
# --- BIBLIOTECA (USUARIO) ---
@login_required
def biblioteca_view(request):
    libros = Biblioteca.objects.all().order_by('-destacado', '-creado_en')
    return render(request, "frontend/biblioteca.html    ", {"libros": libros})

# --- GESTIÓN BIBLIOTECA (ADMIN) ---
@staff_member_required
def gestion_biblioteca(request):
    if not request.user.is_superuser: return redirect("frontend:dashboard")
    
    item_edit = None
    if request.GET.get("edit"):
        item_edit = Biblioteca.objects.filter(id=request.GET.get("edit")).first()

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        destacado = request.POST.get("destacado") == "on"
        pdf = request.FILES.get("archivo_pdf")
        portada = request.FILES.get("imagen_portada")

        if item_edit:
            item_edit.titulo = titulo
            item_edit.descripcion = descripcion
            item_edit.destacado = destacado
            if pdf: item_edit.archivo_pdf = pdf
            if portada: item_edit.imagen_portada = portada
            item_edit.save()
            messages.success(request, "Documento actualizado.")
        else:
            if not pdf:
                messages.error(request, "El archivo PDF es obligatorio.")
            else:
                Biblioteca.objects.create(
                    titulo=titulo,
                    descripcion=descripcion,
                    destacado=destacado,
                    archivo_pdf=pdf,
                    imagen_portada=portada
                )
                messages.success(request, "Documento subido.")
        
        return redirect("frontend:gestion_biblioteca")

    items = Biblioteca.objects.all().order_by('-creado_en')
    return render(request, "frontend/gestion_biblioteca.html", {"items": items, "item_edit": item_edit})

@staff_member_required
def gestion_biblioteca_delete(request, item_id):
    item = get_object_or_404(Biblioteca, id=item_id)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Documento eliminado.")
    return redirect('frontend:gestion_biblioteca')