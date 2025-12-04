"""
Script de prueba para verificar la integración de stock con Wompi

Este script verifica:
1. Que las variantes de productos existen
2. Que el stock se actualiza correctamente
3. Que los movimientos de inventario se registran
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante, Inventario, ItemCarrito, Carrito
from django.contrib.auth import get_user_model
from pagos.utils import actualizar_stock_productos

User = get_user_model()


def crear_producto_prueba():
    """Crea un producto de prueba con variantes"""
    print("\n" + "="*60)
    print("1. CREANDO PRODUCTO DE PRUEBA")
    print("="*60)
    
    # Crear o obtener producto
    producto, created = Producto.objects.get_or_create(
        nombre="Camisa de Prueba Stock",
        defaults={
            'descripcion': 'Producto para probar integración con Wompi',
            'precio': 50000,
            'categoria': 'hombre',
            'destacado': False
        }
    )
    
    if created:
        print(f"✅ Producto creado: {producto.nombre} (ID: {producto.id})")
    else:
        print(f"ℹ️  Producto ya existe: {producto.nombre} (ID: {producto.id})")
    
    # Crear variantes
    variantes_data = [
        {'talla': 'S', 'color': 'Rojo', 'stock': 10},
        {'talla': 'M', 'color': 'Rojo', 'stock': 15},
        {'talla': 'L', 'color': 'Rojo', 'stock': 8},
        {'talla': 'S', 'color': 'Azul', 'stock': 12},
        {'talla': 'M', 'color': 'Azul', 'stock': 20},
        {'talla': 'L', 'color': 'Azul', 'stock': 5},
    ]
    
    variantes_creadas = []
    for data in variantes_data:
        variante, created = ProductoVariante.objects.get_or_create(
            producto=producto,
            talla=data['talla'],
            color=data['color'],
            defaults={
                'stock': data['stock'],
                'tipo_producto': 'ropa'
            }
        )
        
        if created:
            print(f"✅ Variante creada: {variante}")
        else:
            # Actualizar stock si ya existe
            variante.stock = data['stock']
            variante.save()
            print(f"ℹ️  Variante actualizada: {variante}")
        
        variantes_creadas.append(variante)
    
    return producto, variantes_creadas


def probar_actualizacion_stock(producto):
    """Prueba la actualización de stock simulando una compra"""
    print("\n" + "="*60)
    print("2. PROBANDO ACTUALIZACIÓN DE STOCK")
    print("="*60)
    
    # Simular detalle de pedido (como viene de Wompi)
    detalle_pedido = {
        'productos': [
            {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': 2,
                'talla': 'M',
                'color': 'Azul',
                'subtotal': float(producto.precio) * 2
            },
            {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': 1,
                'talla': 'S',
                'color': 'Rojo',
                'subtotal': float(producto.precio)
            }
        ],
        'total': float(producto.precio) * 3,
        'cantidad_items': 2
    }
    
    print(f"\n📦 Simulando compra de:")
    for prod in detalle_pedido['productos']:
        print(f"   - {prod['nombre']} ({prod['talla']}/{prod['color']}) x {prod['cantidad']}")
    
    # Obtener usuario de prueba
    try:
        usuario = User.objects.filter(is_staff=True).first()
        if not usuario:
            usuario = User.objects.first()
    except:
        usuario = None
    
    # Mostrar stock ANTES
    print(f"\n📊 STOCK ANTES:")
    for prod in detalle_pedido['productos']:
        try:
            variante = ProductoVariante.objects.get(
                producto_id=prod['producto_id'],
                talla=prod['talla'],
                color=prod['color']
            )
            print(f"   - {variante.talla}/{variante.color}: {variante.stock} unidades")
        except ProductoVariante.DoesNotExist:
            print(f"   - {prod['talla']}/{prod['color']}: ❌ VARIANTE NO EXISTE")
    
    # Ejecutar actualización
    print(f"\n🔄 Ejecutando actualización de stock...")
    exitoso, mensajes = actualizar_stock_productos(detalle_pedido, usuario)
    
    # Mostrar resultados
    print(f"\n📋 RESULTADOS:")
    for mensaje in mensajes:
        print(f"   {mensaje}")
    
    # Mostrar stock DESPUÉS
    print(f"\n📊 STOCK DESPUÉS:")
    for prod in detalle_pedido['productos']:
        try:
            variante = ProductoVariante.objects.get(
                producto_id=prod['producto_id'],
                talla=prod['talla'],
                color=prod['color']
            )
            print(f"   - {variante.talla}/{variante.color}: {variante.stock} unidades")
        except ProductoVariante.DoesNotExist:
            print(f"   - {prod['talla']}/{prod['color']}: ❌ VARIANTE NO EXISTE")
    
    return exitoso


def verificar_movimientos_inventario(producto):
    """Verifica que se registraron los movimientos de inventario"""
    print("\n" + "="*60)
    print("3. VERIFICANDO MOVIMIENTOS DE INVENTARIO")
    print("="*60)
    
    # Obtener últimos movimientos
    movimientos = Inventario.objects.filter(
        variante__producto=producto
    ).order_by('-fecha')[:10]
    
    if movimientos.exists():
        print(f"\n📝 Últimos {movimientos.count()} movimientos:")
        for mov in movimientos:
            print(f"\n   Variante: {mov.variante.talla}/{mov.variante.color}")
            print(f"   Tipo: {mov.tipo_movimiento}")
            print(f"   Cantidad: {mov.cantidad}")
            print(f"   Stock anterior: {mov.stock_anterior}")
            print(f"   Stock nuevo: {mov.stock_nuevo}")
            print(f"   Fecha: {mov.fecha.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Observaciones: {mov.observaciones}")
    else:
        print("\n⚠️  No se encontraron movimientos de inventario")


def probar_stock_insuficiente(producto):
    """Prueba el caso de stock insuficiente"""
    print("\n" + "="*60)
    print("4. PROBANDO CASO: STOCK INSUFICIENTE")
    print("="*60)
    
    # Simular compra de más unidades de las disponibles
    detalle_pedido = {
        'productos': [
            {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': 100,  # Cantidad muy alta
                'talla': 'L',
                'color': 'Azul',
                'subtotal': float(producto.precio) * 100
            }
        ],
        'total': float(producto.precio) * 100,
        'cantidad_items': 1
    }
    
    print(f"\n📦 Intentando comprar 100 unidades de L/Azul...")
    
    # Mostrar stock actual
    try:
        variante = ProductoVariante.objects.get(
            producto_id=producto.id,
            talla='L',
            color='Azul'
        )
        print(f"   Stock disponible: {variante.stock} unidades")
    except ProductoVariante.DoesNotExist:
        print(f"   ❌ Variante no existe")
        return
    
    # Ejecutar actualización (debería fallar)
    exitoso, mensajes = actualizar_stock_productos(detalle_pedido, None)
    
    print(f"\n📋 RESULTADO:")
    print(f"   Exitoso: {'✅ SÍ' if exitoso else '❌ NO'}")
    for mensaje in mensajes:
        print(f"   {mensaje}")


def probar_variante_inexistente(producto):
    """Prueba el caso de variante inexistente"""
    print("\n" + "="*60)
    print("5. PROBANDO CASO: VARIANTE INEXISTENTE")
    print("="*60)
    
    # Simular compra de variante que no existe
    detalle_pedido = {
        'productos': [
            {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'cantidad': 2,
                'talla': 'XL',  # Talla que no existe
                'color': 'Verde',  # Color que no existe
                'subtotal': float(producto.precio) * 2
            }
        ],
        'total': float(producto.precio) * 2,
        'cantidad_items': 1
    }
    
    print(f"\n📦 Intentando comprar 2 unidades de XL/Verde (no existe)...")
    
    # Ejecutar actualización
    exitoso, mensajes = actualizar_stock_productos(detalle_pedido, None)
    
    print(f"\n📋 RESULTADO:")
    print(f"   Exitoso: {'✅ SÍ' if exitoso else '❌ NO'}")
    for mensaje in mensajes:
        print(f"   {mensaje}")


def main():
    """Función principal que ejecuta todas las pruebas"""
    print("\n" + "="*80)
    print("   SCRIPT DE PRUEBA - INTEGRACIÓN STOCK CON WOMPI")
    print("="*80)
    
    try:
        # 1. Crear producto y variantes
        producto, variantes = crear_producto_prueba()
        
        # 2. Probar actualización exitosa
        exitoso = probar_actualizacion_stock(producto)
        
        # 3. Verificar movimientos
        verificar_movimientos_inventario(producto)
        
        # 4. Probar stock insuficiente
        probar_stock_insuficiente(producto)
        
        # 5. Probar variante inexistente
        probar_variante_inexistente(producto)
        
        # Resumen final
        print("\n" + "="*80)
        print("   RESUMEN DE PRUEBAS")
        print("="*80)
        print(f"\n✅ Producto de prueba: {producto.nombre} (ID: {producto.id})")
        print(f"✅ Variantes creadas: {len(variantes)}")
        print(f"✅ Actualización de stock: {'EXITOSA' if exitoso else 'CON ADVERTENCIAS'}")
        print(f"✅ Casos especiales probados: Stock insuficiente, Variante inexistente")
        print("\n📝 Revisa los logs anteriores para más detalles")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
