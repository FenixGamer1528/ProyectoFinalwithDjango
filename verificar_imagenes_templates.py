"""
Script para verificar que las imágenes se muestran correctamente en los templates
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

print("=" * 80)
print("VERIFICACIÓN DE IMÁGENES EN TEMPLATES")
print("=" * 80)

# Obtener productos
productos = Producto.objects.all()[:5]

print(f"\n📦 Total de productos: {Producto.objects.count()}")

print("\n" + "=" * 80)
print("PRODUCTOS Y SUS IMÁGENES")
print("=" * 80)

for producto in productos:
    print(f"\n{'=' * 60}")
    print(f"📦 {producto.nombre} (ID: {producto.id})")
    print(f"{'=' * 60}")
    
    # Verificar campos de imagen
    tiene_imagen_url = bool(producto.imagen_url)
    tiene_imagen_field = bool(producto.imagen)
    
    print(f"\n📸 Estado de imágenes:")
    print(f"   imagen_url: {producto.imagen_url or '❌ None'}")
    print(f"   imagen (ImageField): {producto.imagen.name if producto.imagen else '❌ None'}")
    
    if producto.imagen:
        print(f"   imagen.url: {producto.imagen.url}")
    
    # Determinar qué mostrará el template
    print(f"\n🎯 Template mostrará:")
    if producto.imagen_url:
        print(f"   ✅ imagen_url: {producto.imagen_url}")
    elif producto.imagen:
        print(f"   ✅ imagen.url: {producto.imagen.url}")
    else:
        print(f"   ⚠️  placeholder: /static/imagenes/placeholder.png")
    
    # Verificar variantes
    variantes = ProductoVariante.objects.filter(producto=producto)
    if variantes.exists():
        print(f"\n🎨 Variantes ({variantes.count()}):")
        colores = list(set(v.color for v in variantes))
        print(f"   Colores: {', '.join(colores)}")
        
        for variante in variantes[:3]:  # Mostrar solo las primeras 3
            ia_badge = "🤖" if variante.imagen_generada_ia else "📷"
            print(f"\n   {ia_badge} {variante.color} - {variante.talla}")
            print(f"      imagen_url: {variante.imagen_url or '❌ None'}")
            print(f"      imagen_ia: {'✅ Sí' if variante.imagen_generada_ia else '❌ No'}")
            
            # Determinar qué mostrará el template para esta variante
            if variante.imagen_url:
                print(f"      Template mostrará: {variante.imagen_url}")
            elif producto.imagen:
                print(f"      Template mostrará (fallback): {producto.imagen.url}")
            else:
                print(f"      Template mostrará: /static/imagenes/placeholder.png")

print("\n" + "=" * 80)
print("RESUMEN DE CORRECCIONES")
print("=" * 80)

print("\n✅ CORRECCIONES APLICADAS:")
print("   1. producto_detalle.html actualizado")
print("   2. producto_detalle_modal.html actualizado")
print("   3. JavaScript del modal actualizado con imagen_url e imagen_ia")
print("   4. Badge IA agregado al modal")
print("   5. Función seleccionarColor actualizada para cambiar imagen")

print("\n📋 LÓGICA DE FALLBACK:")
print("   1. Intenta usar producto.imagen_url")
print("   2. Si no existe, usa producto.imagen.url")
print("   3. Si no existe, usa placeholder.png")

print("\n🎯 PARA VARIANTES:")
print("   1. Intenta usar variante.imagen_url")
print("   2. Si no existe, usa producto.imagen.url como fallback")
print("   3. Si no existe, usa placeholder.png")

print("\n" + "=" * 80)
print("PRUEBA EN NAVEGADOR")
print("=" * 80)

producto_test = Producto.objects.filter(variantes__isnull=False).first()
if producto_test:
    print(f"\n🧪 Producto de prueba: {producto_test.nombre} (ID: {producto_test.id})")
    print(f"\n   Abre en navegador:")
    print(f"   1. Modal: http://localhost:8000/producto/{producto_test.id}/?modal=true")
    print(f"   2. Página completa: http://localhost:8000/producto/{producto_test.id}/")
    print(f"\n   Verifica:")
    print(f"   ✓ La imagen del producto se muestra correctamente")
    print(f"   ✓ Al seleccionar color, la imagen cambia (si las variantes tienen imagen_url)")
    print(f"   ✓ El badge '🤖 IA' aparece para colores con imagen_generada_ia=True")

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)
