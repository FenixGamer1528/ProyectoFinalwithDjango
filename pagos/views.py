from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Transaccion
from .utils import WompiUtils
import json

# Importar modelos de tu app core
from carrito.models import Carrito, ItemCarrito, Pedido

def pagina_pago(request):
    """Vista para redirigir a Wompi Web Checkout"""
    
    # Datos del producto
    monto = 50000  # $50,000 COP
    descripcion = "Compra de producto ejemplo"
    
    # Generar referencia única
    referencia = WompiUtils.generar_referencia()
    
    # Convertir monto a centavos
    monto_en_centavos = int(monto * 100)
    
    # Generar firma de integridad
    firma = WompiUtils.generar_firma_integridad(
        referencia=referencia,
        monto_en_centavos=monto_en_centavos,
        moneda='COP'
    )
    
    # Crear transacción en BD
    transaccion = Transaccion.objects.create(
        referencia=referencia,
        monto=monto,
        estado='PENDING',
        signature=firma
    )
    
    print("="*60)
    print("✅ PAGO CREADO - MÉTODO REDIRECCIÓN")
    print("="*60)
    print(f"Referencia: {referencia}")
    print(f"Monto: ${monto} COP")
    print(f"Firma: {firma}")
    print("="*60)
    
    context = {
        'public_key': settings.WOMPI_PUBLIC_KEY,
        'referencia': referencia,
        'monto': monto,
        'monto_centavos': monto_en_centavos,
        'firma': firma,
        'descripcion': descripcion,
        'transaccion_id': transaccion.id,
        'redirect_url': request.build_absolute_uri('/pagos/confirmacion/')
    }
    
    return render(request, 'pagos/checkout_redirect.html', context)


def confirmar_pago(request):
    """Vista para confirmar el pago después de Wompi"""
    
    transaction_id = request.GET.get('id')
    
    if not transaction_id:
        messages.error(request, 'No se encontró ID de transacción')
        return redirect('pagos:checkout')
    
    # Consultar estado en Wompi
    datos_wompi = WompiUtils.consultar_transaccion(transaction_id)
    
    if not datos_wompi:
        messages.error(request, 'Error al consultar la transacción')
        return redirect('pagos:checkout')
    
    # Actualizar transacción en BD
    try:
        referencia = datos_wompi['data']['reference']
        transaccion = Transaccion.objects.get(referencia=referencia)
        
        transaccion.wompi_transaction_id = transaction_id
        transaccion.wompi_status = datos_wompi['data']['status']
        transaccion.metodo_pago = datos_wompi['data']['payment_method_type']
        transaccion.respuesta_completa = datos_wompi
        
        # Mapear estado
        if datos_wompi['data']['status'] == 'APPROVED':
            transaccion.estado = 'APPROVED'
            messages.success(request, '¡Pago aprobado exitosamente!')
        elif datos_wompi['data']['status'] == 'DECLINED':
            transaccion.estado = 'DECLINED'
            messages.error(request, 'El pago fue rechazado')
        else:
            transaccion.estado = 'PENDING'
            messages.info(request, 'Pago pendiente de confirmación')
        
        transaccion.save()
        
    except Transaccion.DoesNotExist:
        messages.error(request, 'Transacción no encontrada')
        transaccion = None
    
    return render(request, 'pagos/confirmacion.html', {
        'transaccion': transaccion,
        'datos_wompi': datos_wompi
    })


@csrf_exempt
@require_http_methods(["POST"])
def webhook_wompi(request):
    """
    Endpoint para recibir eventos de Wompi
    """
    try:
        # Obtener checksum del header
        checksum_recibido = request.headers.get('X-Event-Checksum', '')
        
        # Parsear JSON
        evento = json.loads(request.body)
        
        print("="*60)
        print("🔔 WEBHOOK RECIBIDO")
        print("="*60)
        print(f"Evento: {evento.get('event')}")
        print("="*60)
        
        # Verificar firma
        if not WompiUtils.verificar_firma_evento(checksum_recibido, evento):
            print("❌ FIRMA INVÁLIDA")
            return JsonResponse({'error': 'Firma inválida'}, status=400)
        
        print("✅ FIRMA VÁLIDA")
        
        # Procesar evento según tipo
        tipo_evento = evento.get('event')
        
        if tipo_evento == 'transaction.updated':
            datos_transaccion = evento['data']['transaction']
            
            try:
                transaccion = Transaccion.objects.get(
                    referencia=datos_transaccion['reference']
                )
                
                transaccion.wompi_transaction_id = datos_transaccion['id']
                transaccion.wompi_status = datos_transaccion['status']
                transaccion.metodo_pago = datos_transaccion.get('payment_method_type', '')
                transaccion.respuesta_completa = datos_transaccion
                
                # Actualizar estado
                if datos_transaccion['status'] == 'APPROVED':
                    transaccion.estado = 'APPROVED'
                    print(f"✅ Transacción APROBADA: {transaccion.referencia}")
                    
                    # 🎉 Crear pedidos si hay detalle
                    if transaccion.detalle_pedido and transaccion.usuario:
                        productos = transaccion.detalle_pedido.get('productos', [])
                        from core.models import Producto
                        
                        for prod_data in productos:
                            try:
                                producto = Producto.objects.get(id=prod_data['producto_id'])
                                Pedido.objects.create(
                                    usuario=transaccion.usuario,
                                    producto=producto,
                                    cantidad=prod_data['cantidad']
                                )
                                print(f"✅ Pedido creado: {producto.nombre}")
                            except Producto.DoesNotExist:
                                print(f"❌ Producto {prod_data['producto_id']} no encontrado")
                        
                        # Vaciar carrito
                        try:
                            carrito = Carrito.objects.get(usuario=transaccion.usuario)
                            carrito.items.all().delete()
                            print(f"✅ Carrito vaciado")
                        except Carrito.DoesNotExist:
                            pass
                    
                elif datos_transaccion['status'] == 'DECLINED':
                    transaccion.estado = 'DECLINED'
                    print(f"❌ Transacción RECHAZADA: {transaccion.referencia}")
                elif datos_transaccion['status'] == 'VOIDED':
                    transaccion.estado = 'VOIDED'
                    print(f"⚠️ Transacción ANULADA: {transaccion.referencia}")
                
                transaccion.save()
                
            except Transaccion.DoesNotExist:
                print(f"❌ Transacción no encontrada: {datos_transaccion['reference']}")
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def historial_transacciones(request):
    """Vista para ver el historial de transacciones"""
    
    if request.user.is_authenticated:
        transacciones = Transaccion.objects.filter(usuario=request.user)
    else:
        transacciones = []
    
    return render(request, 'pagos/historial.html', {
        'transacciones': transacciones
    })
@login_required
def checkout_desde_carrito(request):
    """
    Vista que toma los productos del carrito y crea una transacción de Wompi
    """
    # Obtener carrito del usuario
    try:
        carrito = Carrito.objects.prefetch_related('items__producto').get(usuario=request.user)
        items = carrito.items.all()
        
        if not items.exists():
            messages.error(request, 'Tu carrito está vacío')
            return redirect('ver_carrito')
        
    except Carrito.DoesNotExist:
        messages.error(request, 'No tienes un carrito creado')
        return redirect('index')
    
    # Calcular total del carrito
    total = carrito.total()
    
    if total <= 0:
        messages.error(request, 'El total del carrito debe ser mayor a cero')
        return redirect('ver_carrito')
    
    # Generar referencia única
    referencia = WompiUtils.generar_referencia()
    
    # Convertir total a centavos
    monto_en_centavos = int(float(total) * 100)
    
    # Generar firma de integridad
    firma = WompiUtils.generar_firma_integridad(
        referencia=referencia,
        monto_en_centavos=monto_en_centavos,
        moneda='COP'
    )
    
    # Preparar detalle del pedido (productos del carrito)
    detalle_productos = []
    for item in items:
        detalle_productos.append({
            'producto_id': item.producto.id,
            'nombre': item.producto.nombre,
            'precio': float(item.producto.precio),
            'cantidad': item.cantidad,
            'talla': item.talla,
            'subtotal': float(item.subtotal())
        })
    
    detalle_pedido = {
        'productos': detalle_productos,
        'total': float(total),
        'cantidad_items': items.count()
    }
    
    # Crear transacción en BD
    transaccion = Transaccion.objects.create(
        usuario=request.user,
        referencia=referencia,
        monto=total,
        estado='PENDING',
        signature=firma,
        email=request.user.email,
        nombre_completo=request.user.get_full_name() or request.user.username,
        detalle_pedido=detalle_pedido
    )
    
    print("="*60)
    print("🛒 CHECKOUT DESDE CARRITO")
    print("="*60)
    print(f"Usuario: {request.user.username}")
    print(f"Referencia: {referencia}")
    print(f"Total: ${total} COP")
    print(f"Productos: {len(detalle_productos)}")
    print(f"Firma: {firma}")
    print("="*60)
    
    # Preparar contexto para el template
    context = {
        'public_key': settings.WOMPI_PUBLIC_KEY,
        'referencia': referencia,
        'monto': total,
        'monto_centavos': monto_en_centavos,
        'firma': firma,
        'descripcion': f'Compra de {len(detalle_productos)} producto(s)',
        'transaccion_id': transaccion.id,
        'redirect_url': request.build_absolute_uri('/pagos/confirmacion/'),
        'carrito': carrito,
        'items': items,
        'detalle_productos': detalle_productos
    }
    
    return render(request, 'pagos/checkout_carrito.html', context)


def confirmar_pago_carrito(request):
    """
    Vista mejorada para confirmar el pago y crear los pedidos
    """
    transaction_id = request.GET.get('id')
    
    if not transaction_id:
        messages.error(request, 'No se encontró ID de transacción')
        return redirect('ver_carrito')
    
    # Consultar estado en Wompi
    datos_wompi = WompiUtils.consultar_transaccion(transaction_id)
    
    if not datos_wompi:
        messages.error(request, 'Error al consultar la transacción')
        return redirect('ver_carrito')
    
    # Actualizar transacción en BD
    try:
        referencia = datos_wompi['data']['reference']
        transaccion = Transaccion.objects.get(referencia=referencia)
        
        transaccion.wompi_transaction_id = transaction_id
        transaccion.wompi_status = datos_wompi['data']['status']
        transaccion.metodo_pago = datos_wompi['data']['payment_method_type']
        transaccion.respuesta_completa = datos_wompi
        
        # Mapear estado
        if datos_wompi['data']['status'] == 'APPROVED':
            transaccion.estado = 'APPROVED'
            
            # 🎉 PAGO APROBADO: Crear pedidos y vaciar carrito
            if transaccion.detalle_pedido and transaccion.usuario:
                productos = transaccion.detalle_pedido.get('productos', [])
                
                # Crear un pedido por cada producto
                for prod_data in productos:
                    from core.models import Producto
                    try:
                        producto = Producto.objects.get(id=prod_data['producto_id'])
                        Pedido.objects.create(
                            usuario=transaccion.usuario,
                            producto=producto,
                            cantidad=prod_data['cantidad']
                        )
                    except Producto.DoesNotExist:
                        print(f"Producto {prod_data['producto_id']} no encontrado")
                
                # Vaciar el carrito
                try:
                    carrito = Carrito.objects.get(usuario=transaccion.usuario)
                    carrito.items.all().delete()
                    print(f"✅ Carrito vaciado para usuario {transaccion.usuario.username}")
                except Carrito.DoesNotExist:
                    pass
            
            messages.success(request, '¡Pago aprobado exitosamente! Tu pedido ha sido registrado.')
            
        elif datos_wompi['data']['status'] == 'DECLINED':
            transaccion.estado = 'DECLINED'
            messages.error(request, 'El pago fue rechazado. Por favor intenta con otro método de pago.')
        else:
            transaccion.estado = 'PENDING'
            messages.info(request, 'Pago pendiente de confirmación')
        
        transaccion.save()
        
    except Transaccion.DoesNotExist:
        messages.error(request, 'Transacción no encontrada')
        transaccion = None
    
    return render(request, 'pagos/confirmacion_carrito.html', {
        'transaccion': transaccion,
        'datos_wompi': datos_wompi
    })
