"""
Script de prueba para crear un pedido manualmente y verificar que aparece en el dashboard
"""

from django.contrib.auth import get_user_model
from carrito.models import Pedido, Producto

User = get_user_model()

# Obtener o crear usuario de prueba
usuario = User.objects.first()
producto = Producto.objects.first()

if usuario and producto:
    # Crear pedido de prueba
    pedido = Pedido.objects.create(
        usuario=usuario,
        producto=producto,
        cantidad=2,
        total=producto.precio * 2,
        estado='pendiente',
        telefono=usuario.telefono or '3001234567',
        direccion='Calle de prueba 123',
        ciudad='Bogotá',
        codigo_postal='110111',
        notas='Pedido de prueba para verificar el dashboard'
    )
    
    print("=" * 60)
    print("✅ PEDIDO DE PRUEBA CREADO")
    print("=" * 60)
    print(f"Número: {pedido.numero}")
    print(f"Usuario: {pedido.usuario.username}")
    print(f"Producto: {pedido.producto.nombre}")
    print(f"Cantidad: {pedido.cantidad}")
    print(f"Total: ${pedido.total}")
    print(f"Estado: {pedido.get_estado_display()}")
    print(f"Fecha: {pedido.fecha}")
    print("=" * 60)
    print(f"\n🔗 Verifica en: http://127.0.0.1:8000/dashboard/pedidos/")
    print("=" * 60)
    
    # Verificar que se puede consultar
    pedidos_total = Pedido.objects.count()
    print(f"\n📊 Total de pedidos en la base de datos: {pedidos_total}")
    
else:
    print("❌ No hay usuarios o productos en la base de datos")
    print("Por favor crea al menos un usuario y un producto primero")
