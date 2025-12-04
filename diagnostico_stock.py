"""
Script de diagnóstico para el sistema de stock
Verifica qué datos se están guardando en el carrito y en las transacciones
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Carrito, ItemCarrito, ProductoVariante
from pagos.models import Transaccion
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*80)
print("DIAGNÓSTICO DEL SISTEMA DE STOCK")
print("="*80)

# 1. Verificar items en carritos
print("\n1. ITEMS EN CARRITOS:")
print("-" * 80)
items = ItemCarrito.objects.select_related('carrito__usuario', 'producto').all()[:10]

if items.exists():
    for item in items:
        print(f"\nItem ID: {item.id}")
        print(f"Usuario: {item.carrito.usuario.username}")
        print(f"Producto: {item.producto.nombre}")
        print(f"Talla: {item.talla or 'NO DEFINIDA'}")
        print(f"Color: {item.color or 'NO DEFINIDA'}")
        print(f"Cantidad: {item.cantidad}")
else:
    print("No hay items en carritos")

# 2. Verificar transacciones recientes
print("\n\n2. TRANSACCIONES RECIENTES:")
print("-" * 80)
transacciones = Transaccion.objects.filter(
    detalle_pedido__isnull=False
).order_by('-creado')[:5]

if transacciones.exists():
    for trans in transacciones:
        print(f"\nTransacción: {trans.referencia}")
        print(f"Estado: {trans.estado}")
        print(f"Usuario: {trans.usuario.username if trans.usuario else 'N/A'}")
        
        if trans.detalle_pedido:
            productos = trans.detalle_pedido.get('productos', [])
            print(f"Productos en detalle: {len(productos)}")
            
            for prod in productos:
                print(f"\n  - Producto ID: {prod.get('producto_id')}")
                print(f"    Nombre: {prod.get('nombre')}")
                print(f"    Talla: {prod.get('talla', 'NO DEFINIDA')}")
                print(f"    Color: {prod.get('color', 'NO DEFINIDA')}")
                print(f"    Cantidad: {prod.get('cantidad')}")
else:
    print("No hay transacciones con detalle")

# 3. Verificar variantes existentes
print("\n\n3. VARIANTES DE PRODUCTOS:")
print("-" * 80)
variantes = ProductoVariante.objects.select_related('producto').all()[:10]

if variantes.exists():
    for variante in variantes:
        print(f"\nProducto: {variante.producto.nombre}")
        print(f"Talla: {variante.talla}")
        print(f"Color: {variante.color}")
        print(f"Stock: {variante.stock}")
else:
    print("No hay variantes de productos definidas")

# 4. Verificar si hay desajustes
print("\n\n4. ANÁLISIS DE PROBLEMAS:")
print("-" * 80)

# Contar items sin talla/color
items_sin_talla = ItemCarrito.objects.filter(talla__isnull=True).count()
items_sin_color = ItemCarrito.objects.filter(color__isnull=True).count()

print(f"Items en carrito sin talla: {items_sin_talla}")
print(f"Items en carrito sin color: {items_sin_color}")

# Contar transacciones sin talla/color en detalle
trans_con_problema = 0
for trans in Transaccion.objects.filter(detalle_pedido__isnull=False):
    if trans.detalle_pedido:
        productos = trans.detalle_pedido.get('productos', [])
        for prod in productos:
            if not prod.get('talla') or not prod.get('color'):
                trans_con_problema += 1
                break

print(f"Transacciones con productos sin talla/color: {trans_con_problema}")

# Verificar si hay variantes
total_variantes = ProductoVariante.objects.count()
print(f"Total de variantes de productos: {total_variantes}")

if total_variantes == 0:
    print("\n⚠️ PROBLEMA CRÍTICO: No hay variantes de productos definidas!")
    print("   El sistema necesita variantes para actualizar el stock.")
    print("   Debes crear variantes en el admin para cada producto.")

if items_sin_talla > 0 or items_sin_color > 0:
    print("\n⚠️ ADVERTENCIA: Hay items en carritos sin talla/color definidos")
    print("   Estos items NO podrán actualizar el stock de variantes.")

print("\n" + "="*80)
print("FIN DEL DIAGNÓSTICO")
print("="*80 + "\n")
