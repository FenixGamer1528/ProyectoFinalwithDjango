"""
Script de diagnóstico para verificar el estado de los pedidos después de un pago en Wompi
"""

from carrito.models import Pedido, Producto
from pagos.models import Transaccion
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("🔍 DIAGNÓSTICO DE PEDIDOS Y TRANSACCIONES")
print("=" * 80)

# 1. Verificar transacciones
print("\n📋 TRANSACCIONES EN LA BASE DE DATOS:")
print("-" * 80)
transacciones = Transaccion.objects.all().order_by('-created_at')
if transacciones.exists():
    for i, t in enumerate(transacciones[:5], 1):
        print(f"\n{i}. Transacción: {t.referencia}")
        print(f"   Estado: {t.estado}")
        print(f"   Usuario: {t.usuario.username if t.usuario else 'Sin usuario'}")
        print(f"   Monto: ${t.monto}")
        print(f"   Fecha: {t.created_at}")
        print(f"   Wompi Status: {t.wompi_status or 'N/A'}")
        if t.detalle_pedido:
            productos = t.detalle_pedido.get('productos', [])
            print(f"   Productos en detalle: {len(productos)}")
            for p in productos:
                print(f"      - {p.get('nombre')} x{p.get('cantidad')}")
else:
    print("❌ No hay transacciones registradas")

# 2. Verificar pedidos
print("\n\n📦 PEDIDOS EN LA BASE DE DATOS:")
print("-" * 80)
pedidos = Pedido.objects.all().order_by('-fecha')
if pedidos.exists():
    print(f"Total de pedidos: {pedidos.count()}\n")
    for i, p in enumerate(pedidos[:10], 1):
        print(f"{i}. Pedido: {p.numero}")
        print(f"   Usuario: {p.usuario.username}")
        print(f"   Producto: {p.producto.nombre}")
        print(f"   Cantidad: {p.cantidad}")
        print(f"   Total: ${p.total}")
        print(f"   Estado: {p.get_estado_display()}")
        print(f"   Fecha: {p.fecha}")
        print()
else:
    print("❌ No hay pedidos registrados")

# 3. Verificar transacciones APROBADAS sin pedidos
print("\n\n⚠️  TRANSACCIONES APROBADAS QUE PODRÍAN NO TENER PEDIDOS:")
print("-" * 80)
transacciones_aprobadas = Transaccion.objects.filter(estado='APPROVED')
if transacciones_aprobadas.exists():
    for t in transacciones_aprobadas:
        if t.usuario:
            pedidos_usuario = Pedido.objects.filter(
                usuario=t.usuario,
                notas__contains=t.referencia
            )
            if not pedidos_usuario.exists():
                print(f"\n⚠️  Transacción sin pedidos: {t.referencia}")
                print(f"   Usuario: {t.usuario.username}")
                print(f"   Monto: ${t.monto}")
                print(f"   Fecha: {t.created_at}")
                if t.detalle_pedido:
                    print(f"   Productos que debería tener: {t.detalle_pedido.get('productos', [])}")
else:
    print("No hay transacciones aprobadas")

# 4. Estadísticas
print("\n\n📊 ESTADÍSTICAS GENERALES:")
print("-" * 80)
print(f"Total usuarios: {User.objects.count()}")
print(f"Total productos: {Producto.objects.count()}")
print(f"Total transacciones: {Transaccion.objects.count()}")
print(f"Transacciones aprobadas: {Transaccion.objects.filter(estado='APPROVED').count()}")
print(f"Total pedidos: {Pedido.objects.count()}")
print(f"Pedidos pendientes: {Pedido.objects.filter(estado='pendiente').count()}")
print(f"Pedidos completados: {Pedido.objects.filter(estado='completado').count()}")

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 80)
