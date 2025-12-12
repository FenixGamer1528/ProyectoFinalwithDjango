import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import ProductoVariante

print("=" * 80)
print("🔍 VERIFICANDO URLs DE VARIANTES DEL VESTIDO")
print("=" * 80)

variantes = ProductoVariante.objects.filter(producto_id=138).order_by('color', 'talla')

for v in variantes:
    print(f"\n📦 Variante {v.id}: {v.color} - Talla {v.talla}")
    print(f"   URL: {v.imagen_url}")
    print(f"   IA: {'✅ Sí' if v.imagen_generada_ia else '❌ No'}")
