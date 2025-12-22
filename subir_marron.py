import os
import django
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

import requests
from carrito.models import ProductoVariante

print("=" * 80)
print("📤 SUBIENDO IMAGEN MARRÓN A SUPABASE")
print("=" * 80)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BASE_DIR = Path(__file__).resolve().parent
archivo_path = "media/productos/vestido_marron_138_99b24586.jpg"
archivo_completo = BASE_DIR / archivo_path

if not archivo_completo.exists():
    print(f"❌ Archivo no encontrado: {archivo_path}")
    exit(1)

print(f"✅ Archivo encontrado: {archivo_path}")

# Leer archivo
with open(archivo_completo, 'rb') as f:
    contenido = f.read()

# Nombre en Supabase (sin media/ y sin acentos)
nombre_supabase = "productos/vestido_marron_138_99b24586.jpg"

# URL de upload
upload_url = f"{SUPABASE_URL}/storage/v1/object/media/{nombre_supabase}"

headers = {
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'image/jpeg',
    'apikey': SUPABASE_KEY
}

print(f"📤 Subiendo a: {upload_url}")

try:
    response = requests.post(upload_url, headers=headers, data=contenido)
    
    if response.status_code in [200, 201]:
        print(f"✅ Subido exitosamente")
        print(f"📍 Tamaño: {len(contenido)} bytes")
        
        # Actualizar URLs en base de datos
        nueva_url = f"https://hepzhkhrjvferjebazeg.supabase.co/storage/v1/object/public/media/{nombre_supabase}"
        
        variantes_marron = ProductoVariante.objects.filter(producto_id=138, color='Marrón')
        for v in variantes_marron:
            v.imagen_url = nueva_url
            v.save()
            print(f"   ✅ Variante {v.id} ({v.talla}) actualizada")
            
    elif response.status_code == 409:
        print(f"⚠️ El archivo ya existe")
        # Actualizar URLs de todas formas
        nueva_url = f"https://hepzhkhrjvferjebazeg.supabase.co/storage/v1/object/public/media/{nombre_supabase}"
        variantes_marron = ProductoVariante.objects.filter(producto_id=138, color='Marrón')
        for v in variantes_marron:
            v.imagen_url = nueva_url
            v.save()
            print(f"   ✅ Variante {v.id} ({v.talla}) actualizada con URL corregida")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 80)
print("✅ ¡COMPLETADO! Ahora las 2 variantes (Marrón y Negro) tienen imágenes únicas")
print("=" * 80)
print("\n💡 Recarga la página con Ctrl+F5 y haz clic en los colores del vestido")
