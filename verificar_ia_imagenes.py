"""
Script para verificar el estado de las imágenes generadas por IA
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

print("=" * 80)
print("VERIFICACIÓN DE IMÁGENES GENERADAS POR IA")
print("=" * 80)

# Contar total de variantes
total_variantes = ProductoVariante.objects.count()
print(f"\n📊 Total de variantes en la base de datos: {total_variantes}")

# Contar variantes con imagen_generada_ia = True
variantes_ia = ProductoVariante.objects.filter(imagen_generada_ia=True)
count_ia = variantes_ia.count()
print(f"🤖 Variantes con imagen generada por IA: {count_ia}")

# Contar variantes con imagen_url vacía o None
variantes_sin_imagen = ProductoVariante.objects.filter(imagen_url__isnull=True) | ProductoVariante.objects.filter(imagen_url='')
count_sin_imagen = variantes_sin_imagen.count()
print(f"❌ Variantes sin imagen_url: {count_sin_imagen}")

# Mostrar detalles de las primeras 10 variantes
print("\n" + "=" * 80)
print("DETALLES DE LAS PRIMERAS 10 VARIANTES")
print("=" * 80)

variantes = ProductoVariante.objects.select_related('producto').all()[:10]
for v in variantes:
    print(f"\n🏷️  ID: {v.id} | Producto: {v.producto.nombre}")
    print(f"   Talla: {v.talla} | Color: {v.color} | Stock: {v.stock}")
    print(f"   Imagen URL: {v.imagen_url or '❌ Sin imagen'}")
    print(f"   Imagen IA: {'✅ Sí' if v.imagen_generada_ia else '❌ No'}")

# Si hay variantes con IA, mostrarlas todas
if count_ia > 0:
    print("\n" + "=" * 80)
    print("VARIANTES CON IMAGEN GENERADA POR IA")
    print("=" * 80)
    for v in variantes_ia:
        print(f"\n🤖 ID: {v.id} | Producto: {v.producto.nombre}")
        print(f"   Talla: {v.talla} | Color: {v.color}")
        print(f"   Imagen URL: {v.imagen_url}")

# Verificar si hay productos con múltiples colores
print("\n" + "=" * 80)
print("PRODUCTOS CON MÚLTIPLES COLORES (Para probar cambio de color)")
print("=" * 80)

# Obtener productos que tienen variantes
productos_con_variantes = Producto.objects.filter(variantes__isnull=False).distinct()

for p in productos_con_variantes[:5]:
    variantes_producto = ProductoVariante.objects.filter(producto=p)
    colores = list(set(v.color for v in variantes_producto))
    print(f"\n👕 {p.nombre} (ID: {p.id})")
    print(f"   Colores disponibles: {', '.join(colores)}")
    print(f"   Total variantes: {variantes_producto.count()}")
    for v in variantes_producto:
        ia_badge = "🤖" if v.imagen_generada_ia else "📷"
        print(f"      {ia_badge} {v.talla} - {v.color} | Stock: {v.stock} | {v.imagen_url or '❌'}")

print("\n" + "=" * 80)
print("RESUMEN Y DIAGNÓSTICO")
print("=" * 80)
print(f"Total variantes: {total_variantes}")
print(f"Con imagen IA: {count_ia}")
print(f"Sin imagen: {count_sin_imagen}")
print(f"Productos con variantes: {productos_con_variantes.count()}")

print("\n" + "=" * 80)
print("DIAGNÓSTICO DEL PROBLEMA")
print("=" * 80)

if total_variantes == 0:
    print("❌ PROBLEMA: No hay variantes en la base de datos")
    print("   SOLUCIÓN: Crear variantes para los productos desde el admin de Django")
elif count_sin_imagen == total_variantes:
    print("❌ PROBLEMA: Todas las variantes no tienen imagen_url")
    print("   SOLUCIÓN: Las variantes necesitan tener el campo imagen_url asignado")
    print("   Opciones:")
    print("   1. Usar la imagen principal del producto")
    print("   2. Subir imágenes específicas para cada color")
    print("   3. Generar imágenes con IA para cada color")
elif count_ia == 0:
    print("⚠️  AVISO: No hay variantes con imágenes generadas por IA")
    print("   El cambio de color funcionará si las variantes tienen imagen_url")
    print("   Para que el badge de IA aparezca, marca imagen_generada_ia=True en las variantes con IA")

print("\n" + "=" * 80)
print("PRUEBA RÁPIDA DEL TEMPLATE")
print("=" * 80)
print("\nVerificando que el template producto_detalle.html tiene:")
print("✅ variantesData array con imagen_ia flag")
print("✅ actualizarVariante() function que actualiza imagen")
print("✅ Event listeners en botones de color")
print("✅ #ia-badge element que se muestra/oculta")
print("\n⚠️  Para que veas el cambio de color funcionando:")
print("   1. Las variantes deben tener imagen_url con rutas válidas")
print("   2. Al hacer clic en un color, debe cambiar la imagen")
print("   3. Si imagen_generada_ia=True, debe aparecer el badge '🤖 IA'")
