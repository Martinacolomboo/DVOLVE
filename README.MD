# 🚀 [Dvolve]

Plataforma web desarrollada en **Django** para la gestión de clientes y planes de entrenamiento. El sistema permite la administración de usuarios, control de pagos y gestión dinámica de precios.

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3 + Django
* **Base de Datos:** SQLite (Local) / PostgreSQL (Producción en Render)
* **Almacenamiento de Medios:** Cloudinary (Imágenes y Videos)
* **Frontend:** HTML5, CSS3, JavaScript (Bootstrap)
* **Despliegue:** Render

---

## ⚙️ Instalación y Configuración Local

Si querés correr este proyecto en tu computadora, seguí estos pasos:

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DE_LA_CARPETA>

## Paso 2:Es recomendable usar un entorno virtual para no mezclar librerías
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
#Paso 3: instalar librerias
pip install -r requirements.txt
#Paso 4: Configuarar variables de entorno (.env)
DEBUG=True
SECRET_KEY=tu_clave_secreta_de_django
ALLOWED_HOSTS=*

# Configuración de Cloudinary (Imágenes/Videos)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
#paso 5:Migraciones de base de datos
python manage.py makemigrations
python manage.py migrate
#paso 6: crear un superusuario
python manage.py createsuperuser
#paso 7:correr servidor
python manage.py runserver

💰 Funcionalidades Clave
Gestión de Precios Dinámica
El sistema cuenta con un módulo personalizado para administrar los costos de los planes sin tocar el código.

Ubicación: Panel de Administración o /gestion_admin.

Historial: Se guarda un registro de quién cambió el precio y cuándo.

Frontend: Los precios en la Landing Page se actualizan automáticamente según el último valor cargado.

Carga de Archivos (Cloudinary)
Las imágenes y videos se alojan externamente para optimizar la velocidad y el espacio del servidor.

🚀 Despliegue (Deploy)
El proyecto está configurado para desplegarse automáticamente en Render. Cada vez que se hace un push a la rama main, Render detecta los cambios, corre las migraciones y actualiza el sitio.

Variables de Entorno en Producción: En el dashboard de Render, asegurarse de cargar las mismas variables que en el .env local, más la DATABASE_URL interna.


***

### ⚠️ ¡Un paso clave antes de guardar esto!

Para que el punto 3 (`pip install...`) funcione de verdad, tenés que generar el archivo de requisitos con lo que tenés instalado ahora en tu compu.

Abrí tu terminal y escribí esto **ya mismo**:

```bash
pip freeze > requirements.txt
Esto va a crear el archivo requirements.txt con la lista exacta de librerías (Django, cloudinary, etc.) que estás usando.