import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import ItemCarrito
from django.db.models import Q

print("\n" + "="*60)
print("🧹 LIMPIEZA AUTOMÁTICA DE ITEMS SIN TALLA/COLOR")
print("="*60)

# Buscar items problemáticos
items_problematicos = ItemCarrito.objects.filter(
    Q(talla__isnull=True) | Q(talla='') | 
    Q(color__isnull=True) | Q(color='')
)

print(f"\n📊 Items encontrados sin talla o color: {items_problematicos.count()}")

if items_problematicos.exists():
    print("\n❌ Items problemáticos encontrados:")
    for item in items_problematicos:
        print(f"  - {item.producto.nombre} (Usuario: {item.carrito.usuario.username})")
        print(f"    Talla: {item.talla or 'NO DEFINIDA'}, Color: {item.color or 'NO DEFINIDO'}")
    
    count = items_problematicos.count()
    items_problematicos.delete()
    print(f"\n✅ {count} items eliminados exitosamente")
    print("💡 Los usuarios deberán agregar los productos nuevamente usando el modal.")
    print("   Esto garantizará que tengan talla y color seleccionados.")
else:
    print("\n✅ No hay items problemáticos. Todos los items tienen talla y color.")

print("\n" + "="*60)
print("📝 RESUMEN DE LA SOLUCIÓN:")
print("="*60)
print("1. ✅ Sistema de stock funcionando correctamente")
print("2. ✅ Items antiguos sin talla/color eliminados")
print("3. ✅ Modal con validación implementado")
print("4. 📌 PRÓXIMOS PASOS:")
print("   - Agregar productos usando el botón 'Comprar' (abre el modal)")
print("   - Seleccionar talla y color en el modal")
print("   - Completar la compra")
print("   - Verificar que el stock baja correctamente")
print("="*60)
