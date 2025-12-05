"""
Script para asignar imágenes a las variantes que no tienen imagen_url
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

print("=" * 80)
print("ASIGNACIÓN AUTOMÁTICA DE IMÁGENES A VARIANTES")
print("=" * 80)

# Obtener variantes sin imagen_url
variantes_sin_imagen = ProductoVariante.objects.filter(imagen_url__isnull=True) | ProductoVariante.objects.filter(imagen_url='')
total_sin_imagen = variantes_sin_imagen.count()

print(f"\n📊 Variantes sin imagen_url: {total_sin_imagen}")

if total_sin_imagen == 0:
    print("✅ Todas las variantes ya tienen imagen_url asignada")
    exit()

print("\n" + "=" * 80)
print("ASIGNANDO IMÁGENES...")
print("=" * 80)

actualizadas = 0
for variante in variantes_sin_imagen:
    producto = variante.producto
    
    # Intentar usar la imagen del producto principal
    if producto.imagen_url:
        variante.imagen_url = producto.imagen_url
        variante.save()
        print(f"✅ Variante {variante.id} ({producto.nombre} - {variante.color} {variante.talla})")
        print(f"   Imagen asignada: {variante.imagen_url}")
        actualizadas += 1
    elif producto.imagen:
        # Si el producto tiene imagen local
        variante.imagen_url = producto.imagen.url
        variante.save()
        print(f"✅ Variante {variante.id} ({producto.nombre} - {variante.color} {variante.talla})")
        print(f"   Imagen local asignada: {variante.imagen_url}")
        actualizadas += 1
    else:
        print(f"⚠️  Variante {variante.id} ({producto.nombre} - {variante.color} {variante.talla})")
        print(f"   No se puede asignar imagen: el producto no tiene imagen")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"Total variantes procesadas: {total_sin_imagen}")
print(f"Imágenes asignadas: {actualizadas}")
print(f"Variantes sin imagen: {total_sin_imagen - actualizadas}")

# Preguntar si marcar algunas como generadas por IA (solo para propósitos de prueba)
print("\n" + "=" * 80)
print("MARCADO DE IMÁGENES COMO GENERADAS POR IA (OPCIONAL)")
print("=" * 80)
print("Para probar la funcionalidad del badge de IA, puedes marcar algunas variantes")
print("como generadas por IA (imagen_generada_ia=True)")
print("\n⚠️  NOTA: Esto es solo para propósitos de prueba. En producción, este campo")
print("   debe ser marcado automáticamente cuando se genere una imagen con IA.")

# Marcar la primera variante como IA (solo para demostración)
primera_variante = ProductoVariante.objects.first()
if primera_variante and primera_variante.imagen_url:
    print(f"\n📝 Marcando variante {primera_variante.id} como generada por IA (para prueba)")
    primera_variante.imagen_generada_ia = True
    primera_variante.save()
    print(f"✅ Variante marcada: {primera_variante.producto.nombre} - {primera_variante.color} {primera_variante.talla}")

print("\n" + "=" * 80)
print("✅ PROCESO COMPLETADO")
print("=" * 80)
print("Ahora puedes:")
print("1. Abrir un producto en el navegador")
print("2. Seleccionar diferentes colores")
print("3. Ver cómo cambia la imagen del producto")
print("4. Ver el badge '🤖 IA' si la variante tiene imagen_generada_ia=True")
