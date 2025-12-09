"""
Script para crear variantes de prueba con múltiples colores
Esto te permitirá probar la funcionalidad de cambio de color
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

print("=" * 80)
print("CREACIÓN DE VARIANTES DE PRUEBA CON MÚLTIPLES COLORES")
print("=" * 80)

# Obtener un producto existente
producto = Producto.objects.first()

if not producto:
    print("❌ No hay productos en la base de datos")
    exit()

print(f"\n📦 Producto seleccionado: {producto.nombre} (ID: {producto.id})")
print(f"   Imagen: {producto.imagen_url or producto.imagen.url if producto.imagen else 'Sin imagen'}")

# Definir colores y tallas para las variantes
colores = ['Negro', 'Blanco', 'Azul', 'Rojo', 'Verde']
tallas = ['S', 'M', 'L', 'XL']

# Obtener la imagen del producto
imagen_base = producto.imagen_url if producto.imagen_url else (producto.imagen.url if producto.imagen else None)

if not imagen_base:
    print("❌ El producto no tiene imagen asignada")
    exit()

print(f"\n📸 Usando imagen base: {imagen_base}")

# Eliminar variantes existentes del producto (para empezar limpio)
variantes_existentes = ProductoVariante.objects.filter(producto=producto)
count_eliminadas = variantes_existentes.count()
variantes_existentes.delete()
print(f"\n🗑️  Eliminadas {count_eliminadas} variantes existentes")

print("\n" + "=" * 80)
print("CREANDO VARIANTES...")
print("=" * 80)

creadas = 0
for i, color in enumerate(colores):
    for j, talla in enumerate(tallas):
        # Crear variante
        variante = ProductoVariante.objects.create(
            producto=producto,
            color=color,
            talla=talla,
            stock=10 + (i * 5),  # Stock variable para cada color
            imagen_url=imagen_base,
            # Marcar las primeras 2 variantes como generadas por IA (para prueba)
            imagen_generada_ia=(i < 2)  # Negro y Blanco tendrán el badge de IA
        )
        
        ia_badge = "🤖" if variante.imagen_generada_ia else "📷"
        print(f"{ia_badge} Variante {variante.id}: {color} - {talla} | Stock: {variante.stock}")
        creadas += 1

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"✅ Variantes creadas: {creadas}")
print(f"📦 Producto: {producto.nombre}")
print(f"🎨 Colores: {', '.join(colores)}")
print(f"📏 Tallas: {', '.join(tallas)}")
print(f"\n🤖 Variantes con badge IA: Negro y Blanco (todas las tallas)")
print(f"📷 Variantes normales: Azul, Rojo, Verde (todas las tallas)")

print("\n" + "=" * 80)
print("CÓMO PROBAR LA FUNCIONALIDAD")
print("=" * 80)
print(f"1. Abre el producto en tu navegador:")
print(f"   http://localhost:8000/producto/{producto.id}/")
print(f"\n2. Selecciona diferentes colores:")
print(f"   - Al hacer clic en 'Negro' o 'Blanco', debe aparecer el badge '🤖 IA'")
print(f"   - Al hacer clic en otros colores, el badge debe desaparecer")
print(f"\n3. Selecciona diferentes tallas:")
print(f"   - El stock debe actualizarse según la combinación talla-color")
print(f"   - El botón 'Agregar al carrito' debe habilitarse si hay stock")
print(f"\n4. Observa el comportamiento:")
print(f"   - La imagen cambia cuando seleccionas color (ahora todas usan la misma imagen)")
print(f"   - En el futuro, cada color debería tener su propia imagen")
print(f"   - El badge de IA aparece solo en variantes con imagen_generada_ia=True")

print("\n" + "=" * 80)
print("NOTA IMPORTANTE")
print("=" * 80)
print("⚠️  Todas las variantes están usando la misma imagen por ahora.")
print("   Para ver un cambio visual real de color, deberías:")
print("   1. Subir imágenes diferentes para cada color")
print("   2. O generar imágenes con IA para cada color")
print("   3. Actualizar el campo imagen_url de cada variante")
print("\n   La funcionalidad de cambio está funcionando correctamente,")
print("   solo necesitas imágenes diferentes para cada color.")
