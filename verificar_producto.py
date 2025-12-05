"""
Script para verificar el último producto creado y sus imágenes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto

def verificar_ultimo_producto():
    """Muestra información del último producto creado"""
    try:
        producto = Producto.objects.latest('id')
        
        print("=" * 60)
        print("ÚLTIMO PRODUCTO CREADO")
        print("=" * 60)
        print(f"ID: {producto.id}")
        print(f"Nombre: {producto.nombre}")
        print(f"Categoría: {producto.categoria}")
        print(f"Precio: ${producto.precio}")
        print(f"Stock: {producto.stock}")
        print(f"Destacado: {producto.destacado}")
        print(f"En oferta: {producto.en_oferta}")
        print("-" * 60)
        print(f"Campo imagen: {producto.imagen}")
        print(f"Campo imagen_url: {producto.imagen_url}")
        print("-" * 60)
        print(f"Descripción: {producto.descripcion[:100]}..." if len(producto.descripcion) > 100 else producto.descripcion)
        print("=" * 60)
        
        # Verificar si hay problema con la imagen
        if not producto.imagen_url and not producto.imagen:
            print("⚠️ PROBLEMA: No hay imagen ni imagen_url configurada")
        elif producto.imagen and not producto.imagen_url:
            print("⚠️ PROBLEMA: Hay imagen local pero no se subió a Supabase")
        elif producto.imagen_url:
            print("✅ OK: Imagen URL configurada correctamente")
            
    except Producto.DoesNotExist:
        print("❌ No hay productos en la base de datos")

if __name__ == '__main__':
    verificar_ultimo_producto()
