import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

print("=" * 80)
print("🔧 ARREGLANDO VARIANTES SIN IMAGEN")
print("=" * 80)

# IDs de las variantes sin imagen
variantes_sin_imagen = [62, 63, 64]

for variante_id in variantes_sin_imagen:
    try:
        variante = ProductoVariante.objects.get(id=variante_id)
        producto = variante.producto
        
        print(f"\n📦 Variante ID {variante_id}: {variante.color} - {variante.talla}")
        print(f"   Producto: {producto.nombre}")
        
        # Verificar que el producto tenga imagen
        if producto.imagen_url or producto.imagen:
            # Asignar la imagen del producto a la variante
            if producto.imagen_url:
                variante.imagen_url = producto.imagen_url
                print(f"   ✅ Asignada imagen_url del producto")
            elif producto.imagen:
                variante.imagen_url = producto.imagen.url
                print(f"   ✅ Asignada imagen del producto")
            
            variante.save()
            print(f"   💾 Guardado correctamente")
        else:
            print(f"   ⚠️ El producto no tiene imagen base")
            
    except ProductoVariante.DoesNotExist:
        print(f"\n❌ Variante ID {variante_id} no encontrada")
    except Exception as e:
        print(f"\n❌ Error con variante ID {variante_id}: {str(e)}")

print("\n" + "=" * 80)
print("✅ ¡Proceso completado!")
print("=" * 80)
