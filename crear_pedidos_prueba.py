# Script para crear pedidos de prueba

from carrito.models import Pedido, Producto, UsuarioPersonalizado
from decimal import Decimal

# Obtener usuario y producto
try:
    usuario = UsuarioPersonalizado.objects.first()
    producto = Producto.objects.first()
    
    if usuario and producto:
        # Crear pedidos de prueba con diferentes estados
        pedidos_prueba = [
            {
                'usuario': usuario,
                'producto': producto,
                'cantidad': 2,
                'total': producto.precio * 2,
                'estado': 'pendiente',
                'direccion': 'Calle Principal #123',
                'telefono': '3001234567',
                'ciudad': 'Bogotá',
                'codigo_postal': '110111',
                'notas': 'Pedido de prueba - Entrega rápida por favor'
            },
            {
                'usuario': usuario,
                'producto': producto,
                'cantidad': 1,
                'total': producto.precio,
                'estado': 'procesando',
                'direccion': 'Carrera 7 #45-67',
                'telefono': '3009876543',
                'ciudad': 'Medellín',
                'codigo_postal': '050001',
                'notas': 'Pedido en proceso de preparación'
            },
            {
                'usuario': usuario,
                'producto': producto,
                'cantidad': 3,
                'total': producto.precio * 3,
                'estado': 'completado',
                'direccion': 'Avenida 15 #89-12',
                'telefono': '3005551234',
                'ciudad': 'Cali',
                'codigo_postal': '760001',
                'notas': 'Pedido completado satisfactoriamente'
            }
        ]
        
        for datos in pedidos_prueba:
            pedido = Pedido(**datos)
            pedido.save()
            print(f"Pedido {pedido.numero} creado: {pedido.get_estado_display()}")
        
        print(f"\n✅ {len(pedidos_prueba)} pedidos de prueba creados exitosamente")
    else:
        print("❌ No hay usuarios o productos disponibles")
        
except Exception as e:
    print(f"❌ Error: {e}")
