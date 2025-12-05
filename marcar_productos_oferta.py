"""
Script opcional: Marcar algunos productos como en oferta para probar la funcionalidad
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto

print("=" * 80)
print("MARCAR PRODUCTOS COMO EN OFERTA (OPCIONAL)")
print("=" * 80)

print("\nEste script te permite marcar productos como en oferta para probar")
print("la funcionalidad de los badges.")

# Mostrar todos los productos disponibles
productos = Producto.objects.all()
print(f"\nProductos disponibles: {productos.count()}")

for i, p in enumerate(productos, 1):
    oferta_status = "SI" if p.en_oferta else "NO"
    destacado_status = "SI" if p.destacado else "NO"
    print(f"{i}. {p.nombre} (ID: {p.id})")
    print(f"   - Categoria: {p.categoria}")
    print(f"   - En oferta: {oferta_status}")
    print(f"   - Destacado: {destacado_status}")

print("\n" + "=" * 80)
print("OPCION 1: Marcar todos los productos NO destacados como en oferta")
print("=" * 80)

productos_no_destacados = Producto.objects.filter(destacado=False)
print(f"\nProductos que se marcarian como oferta: {productos_no_destacados.count()}")
for p in productos_no_destacados:
    print(f"  - {p.nombre}")

respuesta = input("\nDeseas marcar estos productos como en oferta? (s/n): ")

if respuesta.lower() == 's':
    count = productos_no_destacados.update(en_oferta=True)
    print(f"\nExito! {count} producto(s) marcado(s) como en oferta")
    
    print("\nVerifica en el navegador:")
    print("  - http://localhost:8000/ofertas/")
    print("  - http://localhost:8000/hombres/")
    print("  - http://localhost:8000/mujeres/")
else:
    print("\nNo se realizaron cambios.")

print("\n" + "=" * 80)
print("INFO: Para marcar/desmarcar productos individualmente")
print("=" * 80)
print("\nPuedes usar el admin de Django:")
print("  1. http://localhost:8000/admin/")
print("  2. Ir a 'Productos'")
print("  3. Editar un producto")
print("  4. Marcar/desmarcar 'En oferta'")
print("  5. Guardar")
