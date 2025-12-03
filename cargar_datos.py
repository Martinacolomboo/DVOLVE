import os
import django
import random
from django.utils import timezone
from datetime import timedelta
from django.core.files import File

# 1. Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webLula.settings')
django.setup()

# 2. Importar Modelos
from django.contrib.auth.models import User
from principal.models import VerifiedEmail, Pago
from frontend.models import (
    Receta, Video, Plan, PlanArchivo, 
    Recomendacion, Podcast, Biblioteca, Questionario
)

# Carpeta raíz de los archivos
BASE_DIR = 'datos_prueba'

def borrar_datos_anteriores():
    print("🧹 Borrando datos viejos para empezar limpio...")
    # BORRAMOS TODO PARA EVITAR ERRORES DE DUPLICADOS
    Pago.objects.all().delete()           # <--- AGREGADO
    VerifiedEmail.objects.all().delete()  # <--- AGREGADO
    Questionario.objects.all().delete()
    
    User.objects.exclude(is_superuser=True).delete()
    
    Receta.objects.all().delete()
    Video.objects.all().delete()
    Plan.objects.all().delete()
    Recomendacion.objects.all().delete()
    Podcast.objects.all().delete()
    Biblioteca.objects.all().delete()
    # No borramos al superusuario para que puedas entrar

def crear_usuarios_con_cuestionarios():
    print("👤 Creando usuarios con perfiles completos...")
    
    perfiles = [
        {
            "user": "lula_fuerza", "pass": "1234", "email": "fuerza@test.com",
            "dias": 30, "plan": "Mensual",
            "q_goal": "fuerza", "q_level": "avanzado", "q_weight": 65, "q_height": 165
        },
        {
            "user": "lula_cardio", "pass": "1234", "email": "cardio@test.com",
            "dias": 90, "plan": "Trimestral",
            "q_goal": "adiposidad", "q_level": "intermedio", "q_weight": 70, "q_height": 160
        },
        {
            "user": "lula_vencido", "pass": "1234", "email": "vencido@test.com",
            "dias": -5, "plan": "Mensual", 
            "q_goal": "bienestar", "q_level": "nunca", "q_weight": 60, "q_height": 170
        },
    ]

    for p in perfiles:
        # 1. Crear Usuario
        user = User.objects.create_user(username=p["user"], email=p["email"], password=p["pass"])
        
        # 2. Suscripción (VerifiedEmail) - Usamos get_or_create por seguridad
        vencimiento = timezone.now() + timedelta(days=p["dias"])
        VerifiedEmail.objects.get_or_create(
            email=p["email"], 
            defaults={'vencimiento': vencimiento}
        )
        
        # 3. Historial de Pago
        Pago.objects.create(
            user=user, email=p["email"], monto=35000, 
            tipo_plan=p["plan"], estado="exitoso"
        )

        # 4. CUESTIONARIO
        Questionario.objects.create(
            user=user,
            health_conditions="ninguna",
            weight=p["q_weight"],
            height=p["q_height"],
            age=random.randint(20, 40),
            training_goal=p["q_goal"],
            training_level=p["q_level"],
            training_days=3,
            training_place="ambos",
            current_diet="balanceada",
            diet_restrictions="ninguna",
            meals=4,
            hydration="buena"
        )
        estado = "ACTIVO" if p["dias"] > 0 else "VENCIDO"
        print(f"   -> Usuario: {p['user']} ({p['q_goal']}) - Plan: {estado}")

def guardar_archivo(modelo_instancia, campo_archivo, ruta_completa, nombre_archivo):
    """Ayuda a guardar archivos abriéndolos correctamente"""
    try:
        with open(ruta_completa, 'rb') as f:
            getattr(modelo_instancia, campo_archivo).save(nombre_archivo, File(f), save=True)
    except Exception as e:
        print(f"   ⚠️ Error guardando archivo {nombre_archivo}: {e}")

def cargar_todo():
    # --- 1. RECETAS ---
    ruta = os.path.join(BASE_DIR, 'recetas')
    if os.path.exists(ruta):
        print("🍳 Cargando Recetas...")
        for arch in os.listdir(ruta):
            if arch.lower().endswith(('.jpg', '.png', '.jpeg')):
                r = Receta.objects.create(
                    titulo=arch.split('.')[0].replace('_', ' ').title(),
                    descripcion="Receta deliciosa cargada automáticamente.",
                    objetivo=random.choice(['fuerza', 'adiposidad', 'resistencia', 'bienestar']),
                    categoria_comida=random.choice(['almuerzo', 'cena', 'desayuno', 'snack']),
                    calorias=random.randint(200, 600),
                    destacado=random.choice([True, False])
                )
                guardar_archivo(r, 'imagen_portada', os.path.join(ruta, arch), arch)

    # --- 2. VIDEOS ---
    ruta = os.path.join(BASE_DIR, 'videos')
    if os.path.exists(ruta):
        print("🎥 Cargando Videos...")
        archivos = os.listdir(ruta)
        videos_mp4 = [f for f in archivos if f.lower().endswith('.mp4')]
        
        for vid in videos_mp4:
            nombre_base = vid.split('.')[0]
            v = Video.objects.create(
                titulo=nombre_base.replace('_', ' ').title(),
                descripcion="Entrenamiento guiado paso a paso.",
                objetivo=random.choice(['fuerza', 'resistencia', 'estiramiento']),
                nivel=random.choice(['intermedio', 'avanzado']),
                creado_por=User.objects.filter(is_superuser=True).first()
            )
            guardar_archivo(v, 'archivo', os.path.join(ruta, vid), vid)
            
            # Buscar portada con mismo nombre
            for ext in ['.jpg', '.png', '.jpeg']:
                posible_img = f"{nombre_base}{ext}"
                if posible_img in archivos:
                    guardar_archivo(v, 'thumbnail', os.path.join(ruta, posible_img), posible_img)
                    break

    # --- 3. PLANES ---
    ruta = os.path.join(BASE_DIR, 'planes')
    if os.path.exists(ruta):
        print("📋 Cargando Planes...")
        archivos = os.listdir(ruta)
        imagenes = [f for f in archivos if f.lower().endswith(('.jpg', '.png'))]
        pdfs = [f for f in archivos if f.lower().endswith('.pdf')]

        created_plans = []
        for img in imagenes:
            p = Plan.objects.create(
                titulo=img.split('.')[0].replace('_', ' ').title(),
                descripcion="Plan integral de 4 semanas.",
                objetivo=random.choice(['recomposicion', 'deficit', 'hipertrofia']),
                destacado=True,
                creado_por=User.objects.filter(is_superuser=True).first()
            )
            guardar_archivo(p, 'portada', os.path.join(ruta, img), img)
            created_plans.append(p)
        
        # Repartir PDFs
        if created_plans and pdfs:
            for pdf in pdfs:
                plan_destino = random.choice(created_plans)
                pa = PlanArchivo.objects.create(
                    plan=plan_destino,
                    nombre=pdf.split('.')[0].replace('_', ' ').title()
                )
                guardar_archivo(pa, 'archivo', os.path.join(ruta, pdf), pdf)

    # --- 4. COACHING ---
    ruta = os.path.join(BASE_DIR, 'coaching')
    if os.path.exists(ruta):
        print("🧠 Cargando Coaching...")
        for arch in os.listdir(ruta):
            if arch.lower().endswith(('.jpg', '.png')):
                c = Recomendacion.objects.create(
                    titulo=arch.split('.')[0].replace('_', ' ').title(),
                    contenido="Tips de mindset para mejorar tu rendimiento.",
                    categoria=random.choice(['bienestar', 'nutricion']),
                )
                guardar_archivo(c, 'imagen_portada', os.path.join(ruta, arch), arch)

    # --- 5. PODCASTS ---
    ruta = os.path.join(BASE_DIR, 'podcasts')
    if os.path.exists(ruta):
        print("🎙️ Cargando Podcasts...")
        for arch in os.listdir(ruta):
            if arch.lower().endswith(('.jpg', '.png')):
                pod = Podcast.objects.create(
                    titulo=arch.split('.')[0].replace('_', ' ').title(),
                    descripcion="Episodio especial sobre hábitos saludables.",
                    link_externo="https://open.spotify.com/"
                )
                guardar_archivo(pod, 'imagen_portada', os.path.join(ruta, arch), arch)

    # --- 6. BIBLIOTECA ---
    ruta = os.path.join(BASE_DIR, 'biblioteca')
    if os.path.exists(ruta):
        print("📚 Cargando Biblioteca...")
        for arch in os.listdir(ruta):
            if arch.lower().endswith('.pdf'):
                lib = Biblioteca.objects.create(
                    titulo=arch.split('.')[0].replace('_', ' ').title(),
                    descripcion="Material educativo exclusivo.",
                )
                guardar_archivo(lib, 'archivo_pdf', os.path.join(ruta, arch), arch)

if __name__ == '__main__':
    print("🚀 INICIANDO CARGA MASIVA...")
    borrar_datos_anteriores()
    crear_usuarios_con_cuestionarios()
    cargar_todo()
    print("\n✅ ¡CARGA COMPLETA!")