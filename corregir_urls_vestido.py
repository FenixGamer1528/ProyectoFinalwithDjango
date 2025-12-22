import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import ProductoVariante
from django.conf import settings

print("=" * 80)
print("🔧 CORRIGIENDO URLs DE VARIANTES DEL VESTIDO")
print("=" * 80)

# URL base de Supabase desde las otras variantes que funcionan
URL_BASE = "https://hepzhkhrjvferjebazeg.supabase.co/storage/v1/object/public/media"

variantes = ProductoVariante.objects.filter(producto_id=138)

for v in variantes:
    if v.imagen_url and v.imagen_url.startswith('/media/'):
        # Convertir URL relativa a URL absoluta de Supabase
        path_relativo = v.imagen_url.replace('/media/', '')
        url_absoluta = f"{URL_BASE}/{path_relativo}"
        
        print(f"\n📦 Variante {v.id}: {v.color} - {v.talla}")
        print(f"   Antes: {v.imagen_url}")
        print(f"   Después: {url_absoluta}")
        
        v.imagen_url = url_absoluta
        v.save()
        print(f"   ✅ Actualizada")

print("\n" + "=" * 80)
print("✅ ¡URLs CORREGIDAS!")
print("=" * 80)
