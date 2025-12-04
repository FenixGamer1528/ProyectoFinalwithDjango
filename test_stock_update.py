import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import ProductoVariante, Inventario, Producto
from pagos.models import Transaccion
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("🔍 VERIFICACIÓN DE STOCK Y TRANSACCIONES")
print("="*60)

# 1. Verificar productos con variantes
print("\n📦 PRODUCTOS CON VARIANTES:")
print("-"*60)
variantes = ProductoVariante.objects.select_related('producto').all()[:10]
for v in variantes:
    print(f"ID: {v.id} | {v.producto.nombre} | Talla: {v.talla} | Color: {v.color} | Stock: {v.stock}")

# 2. Verificar últimas transacciones aprobadas
print("\n💳 ÚLTIMAS TRANSACCIONES APROBADAS:")
print("-"*60)
transacciones = Transaccion.objects.filter(estado='APPROVED').order_by('-creado')[:5]
for t in transacciones:
    print(f"\nReferencia: {t.referencia}")
    print(f"Usuario: {t.usuario.username if t.usuario else 'Sin usuario'}")
    print(f"Monto: ${t.monto}")
    print(f"Fecha: {t.creado}")
    
    if t.detalle_pedido:
        print(f"Detalle del pedido:")
        productos = t.detalle_pedido.get('productos', [])
        for p in productos:
            print(f"  - Producto ID: {p.get('producto_id')}")
            print(f"    Nombre: {p.get('nombre')}")
            print(f"    Cantidad: {p.get('cantidad')}")
            print(f"    Talla: {p.get('talla', 'NO DEFINIDA')}")
            print(f"    Color: {p.get('color', 'NO DEFINIDO')}")
    else:
        print("❌ Sin detalle_pedido")

# 3. Verificar movimientos de inventario
print("\n📋 ÚLTIMOS MOVIMIENTOS DE INVENTARIO:")
print("-"*60)
movimientos = Inventario.objects.select_related('variante', 'variante__producto').order_by('-fecha')[:10]
if movimientos:
    for m in movimientos:
        print(f"Fecha: {m.fecha}")
        print(f"Producto: {m.variante.producto.nombre}")
        print(f"Talla/Color: {m.variante.talla}/{m.variante.color}")
        print(f"Tipo: {m.tipo_movimiento}")
        print(f"Cantidad: {m.cantidad}")
        print(f"Stock: {m.stock_anterior} → {m.stock_nuevo}")
        print(f"Usuario: {m.usuario.username if m.usuario else 'Sistema'}")
        print(f"Observaciones: {m.observaciones}")
        print("-"*40)
else:
    print("❌ No hay movimientos de inventario registrados")

# 4. Test de actualización manual
print("\n🧪 TEST DE ACTUALIZACIÓN DE STOCK:")
print("-"*60)

# Buscar primera variante con stock
variante_test = ProductoVariante.objects.filter(stock__gt=0).first()
if variante_test:
    print(f"\n📦 Variante de prueba:")
    print(f"Producto: {variante_test.producto.nombre}")
    print(f"Talla: {variante_test.talla}, Color: {variante_test.color}")
    print(f"Stock actual: {variante_test.stock}")
    
    # Simular detalle_pedido
    detalle_test = {
        'productos': [
            {
                'producto_id': variante_test.producto.id,
                'nombre': variante_test.producto.nombre,
                'cantidad': 1,
                'talla': variante_test.talla,
                'color': variante_test.color,
                'precio': float(variante_test.producto.precio)
            }
        ]
    }
    
    print(f"\n🔄 Simulando actualización de stock...")
    from pagos.utils import actualizar_stock_productos
    
    exitoso, mensajes = actualizar_stock_productos(detalle_test, None)
    
    print(f"\n📝 Resultado:")
    for mensaje in mensajes:
        print(mensaje)
    
    # Verificar cambio
    variante_test.refresh_from_db()
    print(f"\n✅ Stock después de actualización: {variante_test.stock}")
    
    # Verificar si se creó movimiento
    ultimo_movimiento = Inventario.objects.filter(variante=variante_test).order_by('-fecha').first()
    if ultimo_movimiento:
        print(f"✅ Movimiento de inventario creado:")
        print(f"   Tipo: {ultimo_movimiento.tipo_movimiento}")
        print(f"   Cantidad: {ultimo_movimiento.cantidad}")
        print(f"   Stock: {ultimo_movimiento.stock_anterior} → {ultimo_movimiento.stock_nuevo}")
else:
    print("❌ No hay variantes con stock para probar")

print("\n" + "="*60)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*60)
