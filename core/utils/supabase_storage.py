import os
from pathlib import Path

# Variable para indicar si queremos usar Supabase
USE_SUPABASE = False

if USE_SUPABASE:
    from supabase import create_client
    from dotenv import load_dotenv
    
    # Cargar variables del archivo .env
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    # Leer las variables de entorno
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Crear cliente de Supabase
    supabase = None
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        print("⚠️ No se pudo cargar SUPABASE_URL o SUPABASE_KEY desde .env")
else:
    supabase = None

def subir_a_supabase(imagen):
    """
    Función temporal que devuelve una URL de ejemplo.
    """
    # Devolver una URL temporal para pruebas
    return "/static/imagenes/zapatos.avif"

    try:
        nombre_archivo = f"productos/{imagen.name}"
        contenido = imagen.read()

        # Subir el archivo
        supabase.storage.from_("media").upload(nombre_archivo, contenido)

        # Obtener la URL pública
        url_publica = supabase.storage.from_("media").get_public_url(nombre_archivo)

        print(f"✅ Imagen subida correctamente a Supabase: {url_publica}")
        return url_publica

    except Exception as e:
        print(f"⚠️ Error al subir imagen a Supabase: {e}")
        return None
