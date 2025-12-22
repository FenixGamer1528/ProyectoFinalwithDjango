import os
import django
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

import requests
from carrito.models import ProductoVariante

print("=" * 80)
print("📤 SUBIENDO IMÁGENES DEL VESTIDO A SUPABASE")
print("=" * 80)

# Obtener credenciales de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Cambiado de SUPABASE_ANON_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: No se encontraron las credenciales de Supabase")
    print("   Verifica que SUPABASE_URL y SUPABASE_ANON_KEY estén configuradas")
    exit(1)

print(f"✅ Supabase URL: {SUPABASE_URL}")
print(f"✅ Supabase Key: {SUPABASE_KEY[:20]}...")

# Archivos locales a subir
BASE_DIR = Path(__file__).resolve().parent
archivos = [
    "media/productos/vestido_marrón_138_99b24586.jpg",
    "media/productos/vestido_negro_138_70da1aba.jpg"
]

for archivo_path in archivos:
    archivo_completo = BASE_DIR / archivo_path
    
    if not archivo_completo.exists():
        print(f"\n❌ Archivo no encontrado: {archivo_path}")
        continue
    
    print(f"\n📤 Subiendo: {archivo_path}")
    
    # Leer archivo
    with open(archivo_completo, 'rb') as f:
        contenido = f.read()
    
    # Nombre en Supabase (sin media/)
    nombre_supabase = archivo_path.replace('media/', '')
    
    # URL de upload
    upload_url = f"{SUPABASE_URL}/storage/v1/object/media/{nombre_supabase}"
    
    headers = {
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'image/jpeg',
        'apikey': SUPABASE_KEY
    }
    
    try:
        # Intentar subir
        response = requests.post(upload_url, headers=headers, data=contenido)
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Subido exitosamente")
            print(f"   📍 Tamaño: {len(contenido)} bytes")
        elif response.status_code == 409:
            print(f"   ⚠️ El archivo ya existe en Supabase")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error al subir: {str(e)}")

print("\n" + "=" * 80)
print("🔍 VERIFICANDO URLs EN LA BASE DE DATOS")
print("=" * 80)

variantes = ProductoVariante.objects.filter(producto_id=138).order_by('color')
for v in variantes:
    print(f"\n{v.color} - {v.talla}:")
    print(f"  {v.imagen_url}")

print("\n" + "=" * 80)
print("✅ ¡PROCESO COMPLETADO!")
print("=" * 80)
print("\n💡 Ahora recarga la página con Ctrl+F5 y prueba el modal del vestido")
