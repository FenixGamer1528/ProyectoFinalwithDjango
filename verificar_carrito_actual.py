import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Carrito, ItemCarrito
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("🛒 VERIFICACIÓN DE ITEMS EN CARRITO ACTUAL")
print("="*60)

# Obtener todos los carritos con items
carritos = Carrito.objects.filter(items__isnull=False).distinct()

for carrito in carritos:
    print(f"\n👤 Usuario: {carrito.usuario.username}")
    print(f"ID Carrito: {carrito.id}")
    print("-"*60)
    
    items = carrito.items.all()
    if items:
        for item in items:
            print(f"  📦 Producto: {item.producto.nombre}")
            print(f"     ID Producto: {item.producto.id}")
            print(f"     Cantidad: {item.cantidad}")
            print(f"     Talla: {item.talla if item.talla else '❌ NO DEFINIDA'}")
            print(f"     Color: {item.color if item.color else '❌ NO DEFINIDO'}")
            print()
    else:
        print("  Carrito vacío")

# Verificar si hay items sin talla o color
items_sin_talla = ItemCarrito.objects.filter(talla__isnull=True) | ItemCarrito.objects.filter(talla='')
items_sin_color = ItemCarrito.objects.filter(color__isnull=True) | ItemCarrito.objects.filter(color='')

print("\n⚠️ ITEMS PROBLEMÁTICOS:")
print("-"*60)
if items_sin_talla.exists():
    print(f"❌ Items sin talla: {items_sin_talla.count()}")
    for item in items_sin_talla:
        print(f"   - {item.producto.nombre} (Usuario: {item.carrito.usuario.username})")

if items_sin_color.exists():
    print(f"❌ Items sin color: {items_sin_color.count()}")
    for item in items_sin_color:
        print(f"   - {item.producto.nombre} (Usuario: {item.carrito.usuario.username})")

if not items_sin_talla.exists() and not items_sin_color.exists():
    print("✅ Todos los items tienen talla y color definidos")

print("\n" + "="*60)
