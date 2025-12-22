import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

# Ver producto corset
producto = Producto.objects.get(id=113)
print(f"Producto: {producto.nombre}")
print(f"Imagen: {producto.imagen}")
print(f"Imagen URL: {getattr(producto, 'imagen_url', 'N/A')}")

print("\n--- Variantes del corset ---")
variantes = ProductoVariante.objects.filter(producto=producto)
for v in variantes:
    print(f"\nVariante ID: {v.id}")
    print(f"  Color: {v.color}")
    print(f"  Talla: {v.talla}")
    print(f"  Imagen: {v.imagen}")
    print(f"  Imagen URL: {getattr(v, 'imagen_url', 'N/A')}")
