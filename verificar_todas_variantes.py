import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

# Obtener todos los productos con variantes
productos = Producto.objects.filter(variantes__isnull=False).distinct()

print("=" * 80)
print("🔍 VERIFICANDO TODAS LAS VARIANTES DEL SISTEMA")
print("=" * 80)

total_productos = 0
total_variantes = 0
variantes_sin_imagen = 0

for producto in productos:
    variantes = ProductoVariante.objects.filter(producto=producto)
    total_productos += 1
    
    print(f"\n📦 {producto.nombre} (ID: {producto.id})")
    print(f"   Variantes: {variantes.count()}")
    
    for v in variantes:
        total_variantes += 1
        tiene_imagen = bool(v.imagen_url or v.imagen)
        icono = "✅" if tiene_imagen else "❌"
        
        if not tiene_imagen:
            variantes_sin_imagen += 1
        
        print(f"   {icono} ID {v.id}: {v.color} - {v.talla} - Stock: {v.stock}")
        
        if tiene_imagen:
            if v.imagen_url:
                print(f"      🖼️ URL: {v.imagen_url[:80]}...")
            elif v.imagen:
                print(f"      🖼️ Archivo: {v.imagen.name}")
        else:
            print(f"      ⚠️ SIN IMAGEN")

print("\n" + "=" * 80)
print(f"📊 RESUMEN:")
print(f"   Productos con variantes: {total_productos}")
print(f"   Total variantes: {total_variantes}")
print(f"   Variantes SIN imagen: {variantes_sin_imagen}")
print(f"   Variantes CON imagen: {total_variantes - variantes_sin_imagen}")
print("=" * 80)

if variantes_sin_imagen > 0:
    print(f"\n⚠️ Hay {variantes_sin_imagen} variantes sin imagen que necesitan corrección")
else:
    print("\n✅ ¡Todas las variantes tienen imagen asignada!")
