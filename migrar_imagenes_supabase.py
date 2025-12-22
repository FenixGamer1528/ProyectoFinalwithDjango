"""
Script OPCIONAL: Migrar imágenes locales existentes a Supabase
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto
from core.utils.supabase_storage import subir_a_supabase, USE_SUPABASE
from django.core.files import File

print("=" * 80)
print("MIGRACION DE IMAGENES LOCALES A SUPABASE")
print("=" * 80)

if not USE_SUPABASE:
    print("\nERROR: Supabase esta deshabilitado")
    print("Habilita USE_SUPABASE = True en core/utils/supabase_storage.py")
    exit(1)

# Obtener productos con imágenes locales pero sin imagen_url
productos_locales = Producto.objects.filter(imagen__isnull=False, imagen_url__isnull=True)

print(f"\nProductos con imagenes locales: {productos_locales.count()}")

if productos_locales.count() == 0:
    print("\nNo hay productos con imagenes locales para migrar")
    print("Todos los productos ya usan Supabase o no tienen imagenes")
    exit(0)

print("\nProductos a migrar:")
for p in productos_locales:
    print(f"  - {p.nombre}: {p.imagen.name}")

respuesta = input("\nDeseas migrar estas imagenes a Supabase? (s/n): ")

if respuesta.lower() != 's':
    print("\nMigracion cancelada")
    exit(0)

print("\n" + "=" * 80)
print("MIGRANDO IMAGENES...")
print("=" * 80)

exitosas = 0
fallidas = 0

for producto in productos_locales:
    try:
        print(f"\nMigrando: {producto.nombre}")
        print(f"  Archivo local: {producto.imagen.name}")
        
        # Abrir el archivo local
        with producto.imagen.open('rb') as imagen_file:
            # Crear un objeto File de Django
            from django.core.files.base import ContentFile
            contenido = imagen_file.read()
            
            # Subir a Supabase
            url = subir_a_supabase(producto.imagen)
            
            if url:
                # Actualizar el producto
                producto.imagen_url = url
                producto.save()
                print(f"  Exito! URL: {url[:70]}...")
                exitosas += 1
                
                # Opcional: eliminar archivo local
                try:
                    producto.imagen.delete(save=False)
                    print(f"  Archivo local eliminado")
                except Exception as e:
                    print(f"  No se pudo eliminar archivo local: {e}")
            else:
                print(f"  Error: No se obtuvo URL de Supabase")
                fallidas += 1
                
    except Exception as e:
        print(f"  Error al migrar: {e}")
        fallidas += 1

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"\nImagenes migradas exitosamente: {exitosas}")
print(f"Imagenes con error: {fallidas}")

if exitosas > 0:
    print("\nLas imagenes ahora estan en Supabase!")
    print("Puedes verificar en: https://hepzhkhrjvferjebazeg.supabase.co/project/default/storage/buckets/media")
