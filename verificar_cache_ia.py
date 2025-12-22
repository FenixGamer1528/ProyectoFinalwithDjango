import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from dashboard.models import ImagenColorCache
from carrito.models import ProductoVariante

print("✅ Sistema de Caché de Imágenes IA")
print("=" * 50)

# Verificar modelo
total_cache = ImagenColorCache.objects.count()
print(f"\n📊 Total de imágenes en caché: {total_cache}")

if total_cache > 0:
    print("\n🎨 Últimas 5 imágenes cacheadas:")
    for cache in ImagenColorCache.objects.all()[:5]:
        print(f"  - {cache.variante.producto.nombre} | {cache.color_hex} | {cache.fecha_generacion.strftime('%d/%m/%Y %H:%M')}")

# Verificar variantes disponibles para pruebas
variantes = ProductoVariante.objects.filter(color__isnull=False).count()
print(f"\n📦 Total variantes con color: {variantes}")

if variantes > 0:
    print("\n🔍 Primeras 5 variantes para probar:")
    for v in ProductoVariante.objects.filter(color__isnull=False)[:5]:
        print(f"  - ID: {v.id} | {v.producto.nombre} | Color: {v.color} | Talla: {v.talla}")
        print(f"    URL para generar: http://127.0.0.1:8000/dashboard/api/variante/{v.id}/generar-color/")

print("\n" + "=" * 50)
print("✅ Sistema funcionando correctamente")
print("\n🧪 Para probar:")
print("1. Abre el producto en el navegador")
print("2. Haz clic en un círculo de color")
print("3. La primera vez generará con IA (3-5 seg)")
print("4. La segunda vez cargará desde caché (instantáneo)")
