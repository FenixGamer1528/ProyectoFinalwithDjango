import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

p = Producto.objects.get(id=105)
variantes = ProductoVariante.objects.filter(producto=p)

print("="*50)
print(f"Producto.colores: '{p.colores}' (tipo: {type(p.colores).__name__})")
print(f"Producto.colores repr: {repr(p.colores)}")
print(f"len(Producto.colores): {len(p.colores) if p.colores else 0}")

print("\nVariantes:")
for v in variantes:
    print(f"  Variante {v.id}: color='{v.color}' (tipo: {type(v.color).__name__})")
    print(f"    repr: {repr(v.color)}")
    
print("\n" + "="*50)
print("SIMULANDO LA VISTA:")
print("="*50)

colores_disponibles = []
if p.colores:
    print(f"✓ Agregando color base: '{p.colores}'")
    colores_disponibles.append(p.colores)
else:
    print(f"✗ p.colores es falsy: {p.colores}")

for v in variantes:
    print(f"\nChecking variante {v.id}:")
    print(f"  v.color = '{v.color}'")
    print(f"  v.color is truthy? {bool(v.color)}")
    print(f"  v.color in colores_disponibles? {v.color in colores_disponibles}")
    
    if v.color and v.color not in colores_disponibles:
        print(f"  ✓ Agregando: '{v.color}'")
        colores_disponibles.append(v.color)
    else:
        print(f"  ✗ NO agregando")

print(f"\n{'='*50}")
print(f"RESULTADO FINAL:")
print(f"colores_disponibles = {colores_disponibles}")
print(f"{'='*50}")
