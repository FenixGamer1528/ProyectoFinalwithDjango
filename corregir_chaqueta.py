"""
Script para corregir el último producto (Chaqueta de cuero) 
y limpiar la imagen_url incorrecta
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto

def corregir_producto():
    """Corrige el producto 'Chaqueta de cuero' eliminando la imagen_url incorrecta"""
    try:
        producto = Producto.objects.get(id=120, nombre="Chaqueta de cuero")
        
        print("=" * 60)
        print("CORRIGIENDO PRODUCTO")
        print("=" * 60)
        print(f"Nombre: {producto.nombre}")
        print(f"Imagen URL actual: {producto.imagen_url}")
        print(f"Campo imagen: {producto.imagen}")
        print("-" * 60)
        
        # Limpiar la imagen_url incorrecta
        producto.imagen_url = None
        producto.save()
        
        print("✅ Imagen URL limpiada")
        print(f"Nueva imagen URL: {producto.imagen_url}")
        print(f"Campo imagen: {producto.imagen}")
        print("=" * 60)
        print("\n⚠️ IMPORTANTE:")
        print("Debes volver a subir la imagen del producto desde el dashboard")
        print("para que se guarde correctamente en el almacenamiento local.")
        print("=" * 60)
        
    except Producto.DoesNotExist:
        print("❌ No se encontró el producto ID 120 'Chaqueta de cuero'")

if __name__ == '__main__':
    corregir_producto()
