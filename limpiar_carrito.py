import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import ItemCarrito
from django.db.models import Q

print("\n" + "="*60)
print("🧹 LIMPIEZA DE ITEMS SIN TALLA/COLOR")
print("="*60)

# Buscar items problemáticos
items_problematicos = ItemCarrito.objects.filter(
    Q(talla__isnull=True) | Q(talla='') | 
    Q(color__isnull=True) | Q(color='')
)

print(f"\n📊 Items encontrados sin talla o color: {items_problematicos.count()}")

if items_problematicos.exists():
    print("\nItems a eliminar:")
    for item in items_problematicos:
        print(f"  - {item.producto.nombre} (Usuario: {item.carrito.usuario.username})")
        print(f"    Talla: {item.talla}, Color: {item.color}")
    
    confirmacion = input("\n¿Deseas eliminar estos items del carrito? (si/no): ")
    
    if confirmacion.lower() == 'si':
        count = items_problematicos.count()
        items_problematicos.delete()
        print(f"\n✅ {count} items eliminados exitosamente")
        print("Los usuarios deberán agregar los productos nuevamente usando el modal")
    else:
        print("\n❌ Operación cancelada")
else:
    print("\n✅ No hay items problemáticos. Todos los items tienen talla y color.")

print("\n" + "="*60)
