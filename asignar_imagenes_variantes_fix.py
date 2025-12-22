import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

# Asignar imagen del producto a las variantes que no tienen
print("Asignando imágenes de producto a variantes sin imagen...")

variantes_sin_imagen = ProductoVariante.objects.filter(imagen_url__isnull=True)
print(f"Total variantes sin imagen: {variantes_sin_imagen.count()}")

for v in variantes_sin_imagen:
    if v.producto.imagen_url:
        v.imagen_url = v.producto.imagen_url
        v.save()
        print(f"✅ {v.producto.nombre} - {v.color} T{v.talla} → {v.imagen_url[:60]}...")
    else:
        print(f"⚠️ {v.producto.nombre} no tiene imagen_url")

print(f"\n✅ Completado: {variantes_sin_imagen.count()} variantes actualizadas")
