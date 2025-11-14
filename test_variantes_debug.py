import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

# Obtener el producto
producto = Producto.objects.get(id=105)
variantes = ProductoVariante.objects.filter(producto=producto)

print(f"=== PRODUCTO ===")
print(f"ID: {producto.id}")
print(f"Nombre: {producto.nombre}")
print(f"Talla base: '{producto.talla}'")
print(f"Color base: '{producto.colores}'")

print(f"\n=== VARIANTES ({variantes.count()}) ===")
for v in variantes:
    print(f"Variante {v.id}: Talla='{v.talla}', Color='{v.color}', Stock={v.stock}")

# Simular la lógica de la vista
print(f"\n=== LÓGICA DE VISTA ===")

tallas_disponibles = []
if producto.talla:
    print(f"✓ Agregando talla base: '{producto.talla}'")
    tallas_disponibles.append(producto.talla)
else:
    print(f"✗ producto.talla está vacío o None")

for v in variantes:
    if v.talla and v.talla not in tallas_disponibles:
        print(f"✓ Agregando talla de variante: '{v.talla}'")
        tallas_disponibles.append(v.talla)

colores_disponibles = []
if producto.colores:
    print(f"✓ Agregando color base: '{producto.colores}'")
    colores_disponibles.append(producto.colores)
else:
    print(f"✗ producto.colores está vacío o None")

for v in variantes:
    if v.color and v.color not in colores_disponibles:
        print(f"✓ Agregando color de variante: '{v.color}'")
        colores_disponibles.append(v.color)

print(f"\n=== RESULTADO FINAL ===")
print(f"tallas_disponibles: {tallas_disponibles}")
print(f"colores_disponibles: {colores_disponibles}")
