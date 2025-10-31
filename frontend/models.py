from django.db import models
from django.contrib.auth.models import User


class Questionario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="questionario_user")

    # ================== ENTRENAMIENTO ==================
    health_conditions = models.CharField(max_length=50, choices=[
        ("hernia", "Hernia"),
        ("escoliosis", "Escoliosis"),
        ("rodilla", "Lesión de rodilla"),
        ("hombro", "Lesión de hombro"),
        ("ninguna", "Ninguna"),
    ], default="ninguna", blank=True, null=True)

    weight = models.FloatField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)

    training_goal = models.CharField(max_length=50, choices=[
        ("resistencia", "Resistencia"),
        ("fuerza", "Ganar fuerza"),
        ("adiposidad", "Bajar adiposidad"),
        ("bienestar", "Bienestar general"),
    ], blank=True, null=True)

    training_level = models.CharField(max_length=50, choices=[
        ("nunca", "Nunca entrené"),
        ("intermedio", "Intermedio"),
        ("avanzado", "Avanzado"),
    ], blank=True, null=True)
    training_place = models.CharField(
        max_length=20,
        choices=[
            ("casa", "En casa"),
            ("gimnasio", "En gimnasio"),
            ("ambos", "Ambos entornos"),
        ],
        default="casa"
    )
    other_activity = models.CharField(max_length=50, choices=[
        ("no", "No"),
        ("correr", "Correr"),
        ("natacion", "Natación"),
        ("ciclismo", "Ciclismo"),
        ("futbol", "Fútbol"),
        ("otra", "Otra"),
    ], default="no")

    training_days = models.IntegerField(blank=True, null=True)
    training_place = models.CharField(
        max_length=20,
        choices=[
            ("casa", "En casa"),
            ("gimnasio", "En gimnasio"),
            ("ambos", "Ambos entornos"),
        ],
        default="casa"
    )
    sleep = models.CharField(max_length=50, choices=[
        ("7-8", "7/8 horas"),
        ("dificil", "Me cuesta descansar"),
    ], blank=True, null=True)

    # ================== ALIMENTACIÓN ==================
    current_diet = models.TextField(
        blank=True,  # permite que quede vacío
        null=True,   # permite que sea nulo en la base de datos
        help_text="Describe tu dieta actual"
    )
    diet_restrictions = models.CharField(max_length=50, choices=[
        ("ninguna", "Ninguna"),
        ("diabetes", "Diabetes"),
        ("celiaquia", "Celiaquía"),
        ("veganismo", "Veganismo"),
        ("vegetarianismo", "Vegetarianismo"),
    ], default="ninguna")
    diet_goal = models.CharField(max_length=255,blank=True,null=True     ) 
    thyroid = models.CharField(max_length=50, choices=[
        ("ninguna", "Ninguna"),
        ("hiper", "Hipertiroidismo"),
        ("hipo", "Hipotiroidismo"),
    ], default="ninguna")

    meals = models.IntegerField(blank=True, null=True)

    snacks = models.CharField(max_length=10, choices=[
        ("si", "Sí"),
        ("no", "No"),
    ], default="no")

    meal_schedule = models.CharField(max_length=20, choices=[
        ("regulares", "Regulares"),
        ("irregulares", "No regulables"),
    ], default="regulares")

    hydration = models.CharField(max_length=20, choices=[
        ("poca", "Consumo poca agua"),
        ("buena", "Consumo buena cantidad"),
    ], default="poca")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cuestionario de {self.user.username}"

class Video(models.Model):
    OBJETIVOS = [
        ("resistencia", "Resistencia"),
        ("fuerza", "Fuerza"),
        ("adiposidad", "Bajar adiposidad"),
        ("bienestar", "Bienestar general"),
    ]
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to="videos/")  
    thumbnail = models.ImageField(upload_to="videos/thumbnails/", blank=True, null=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # 👈 acá
    destacado = models.BooleanField(default=False)  # 👈 recomendado para dashboard
    objetivo = models.CharField(max_length=50, choices=OBJETIVOS, blank=True, null=True)  # 👈 relacion con cuestionario
    nivel = models.CharField(max_length=50, choices=[
        ("nunca", "Nunca entrené"),
        ("intermedio", "Intermedio"),
        ("avanzado", "Avanzado"),
    ], blank=True, null=True)
    entorno = models.CharField(
        max_length=20,
        choices=[
            ("casa", "En casa"),
            ("gimnasio", "En gimnasio"),
            ("ambos", "Ambos entornos"),
        ],
        default="ambos"
    )
    apto_para = models.CharField(
        max_length=50,
        choices=[
            ("ninguna", "Sin restricciones"),
            ("hernia", "Apto para personas con hernia"),
            ("rodilla", "Apto para lesión de rodilla"),
            ("hombro", "Apto para lesión de hombro"),
        ],
        default="ninguna"
    )
    requiere_equipo = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Receta(models.Model):
    OBJETIVOS = [
        ("resistencia", "Resistencia"),
        ("fuerza", "Fuerza"),
        ("adiposidad", "Bajar adiposidad"),
        ("bienestar", "Bienestar general"),
    ]

    RESTRICCIONES = [
        ("ninguna", "Ninguna"),
        ("diabetes", "Diabetes"),
        ("celiaquia", "Celiaquía"),
        ("veganismo", "Veganismo"),
        ("vegetarianismo", "Vegetarianismo"),
    ]

    TIROIDES = [
        ("ninguna", "Ninguna"),
        ("hiper", "Hipertiroidismo"),
        ("hipo", "Hipotiroidismo"),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to="recetas/")
    creado_en = models.DateTimeField(auto_now_add=True)

    objetivo = models.CharField(max_length=50, choices=OBJETIVOS, blank=True, null=True)
    categoria_comida = models.CharField(
        max_length=20,
        choices=[
            ("desayuno", "Desayuno"),
            ("almuerzo", "Almuerzo"),
            ("cena", "Cena"),
            ("snack", "Snack"),
            ("post-entreno", "Post-entreno"),
        ],
        default="almuerzo",
        verbose_name="Tipo de Comida"
    )

    # 👇 NUEVOS CAMPOS
    diet_restrictions = models.CharField(
        max_length=50, choices=RESTRICCIONES, default="ninguna", verbose_name="Restricción Alimentaria"
    )
    thyroid = models.CharField(
        max_length=50, choices=TIROIDES, default="ninguna", verbose_name="Patología de Tiroides"
    )

    destacado = models.BooleanField(default=False)
    imagen_portada = models.ImageField(upload_to="recetas/portadas/", blank=True, null=True)

    # Valores nutricionales
    tiempo_prep = models.IntegerField(blank=True, null=True)
    porciones = models.IntegerField(blank=True, null=True)
    calorias = models.IntegerField(blank=True, null=True)
    proteinas = models.IntegerField(blank=True, null=True)
    carbohidratos = models.IntegerField(blank=True, null=True)
    grasas = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.titulo

class Recomendacion(models.Model):
    CATEGORIAS = [
        ("entrenamiento", "Entrenamiento"),
        ("nutricion", "Nutrición"),
        ("bienestar", "Bienestar"),
    ]

    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default="bienestar")
    creado_en = models.DateTimeField(auto_now_add=True)
    destacado = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.titulo} ({self.categoria})"

