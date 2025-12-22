import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

print("=" * 80)
print("🔍 COMPARANDO IMÁGENES DE BOTAS vs VESTIDO")
print("=" * 80)

# Botas Slouch
botas = Producto.objects.get(id=136)
print(f"\n📦 {botas.nombre}")
print(f"   Imagen base: {botas.imagen_url[:60]}...")
variantes_botas = ProductoVariante.objects.filter(producto=botas)
for v in variantes_botas:
    print(f"   • {v.color} {v.talla}: {v.imagen_url[:60] if v.imagen_url else 'SIN IMAGEN'}...")

# Botas Plataforma
plataforma = Producto.objects.get(id=135)
print(f"\n📦 {plataforma.nombre}")
print(f"   Imagen base: {plataforma.imagen_url[:60]}...")
variantes_plat = ProductoVariante.objects.filter(producto=plataforma)
for v in variantes_plat:
    print(f"   • {v.color} {v.talla}: {v.imagen_url[:60] if v.imagen_url else 'SIN IMAGEN'}...")

# Vestido
vestido = Producto.objects.get(id=138)
print(f"\n📦 {vestido.nombre}")
print(f"   Imagen base: {vestido.imagen_url[:60]}...")
variantes_vestido = ProductoVariante.objects.filter(producto=vestido)
for v in variantes_vestido:
    print(f"   • {v.color} {v.talla}: {v.imagen_url[:60] if v.imagen_url else 'SIN IMAGEN'}...")

print("\n" + "=" * 80)
print("🔍 ANÁLISIS:")
print("=" * 80)

# Verificar si las URLs son diferentes
urls_botas = set([v.imagen_url for v in variantes_botas if v.imagen_url])
urls_vestido = set([v.imagen_url for v in variantes_vestido if v.imagen_url])

print(f"\n✅ Botas Slouch: {len(urls_botas)} imágenes ÚNICAS")
print(f"❌ Vestido: {len(urls_vestido)} imágenes únicas")

if len(urls_vestido) == 1:
    print("\n⚠️ PROBLEMA DETECTADO:")
    print("   Todas las variantes del Vestido tienen la MISMA imagen")
    print("   Por eso no se ve el cambio al hacer clic en los colores")
    print("\n💡 SOLUCIÓN:")
    print("   Necesitas asignar imágenes diferentes para cada color del Vestido")
