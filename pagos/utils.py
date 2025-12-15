import hashlib
import hmac
import requests
from django.conf import settings
from datetime import datetime
import random
import string

class WompiUtils:
    """Utilidades para integración con Wompi"""
    
    BASE_URL_TEST = 'https://sandbox.wompi.co/v1'
    BASE_URL_PROD = 'https://production.wompi.co/v1'
    
    @staticmethod
    def get_base_url():
        """Obtener URL base según ambiente"""
        return WompiUtils.BASE_URL_TEST if settings.WOMPI_ENV == 'TEST' else WompiUtils.BASE_URL_PROD
    
    @staticmethod
    def generar_referencia():
        """Genera una referencia única para la transacción"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"REF_{timestamp}_{random_str}"
    
    @staticmethod
    def generar_firma_integridad(referencia, monto_en_centavos, moneda='COP'):
        """
        Genera la firma de integridad SHA256 usando el INTEGRITY SECRET
        Concatenación: referencia + monto_en_centavos + moneda + integrity_secret
        """
        # IMPORTANTE: Usar INTEGRITY SECRET, no PRIVATE KEY
        integrity_secret = settings.WOMPI_INTEGRITY_SECRET
        
        # Convertir monto a string sin decimales
        monto_str = str(int(monto_en_centavos))
        
        # Concatenar: referencia + monto + moneda + integrity_secret
        cadena = f"{referencia}{monto_str}{moneda}{integrity_secret}"
        
        # Generar SHA256
        firma = hashlib.sha256(cadena.encode('utf-8')).hexdigest()
        
        return firma
    
    @staticmethod
    def verificar_firma_evento(checksum_recibido, evento_json):
        """
        Verifica la firma de un evento webhook usando EVENTS SECRET
        """
        # Extraer propiedades según el evento
        properties = evento_json['signature']['properties']
        timestamp = evento_json['timestamp']
        
        # Construir cadena concatenando valores de las propiedades
        valores = []
        data = evento_json['data']
        
        for prop in properties:
            keys = prop.split('.')
            valor = data
            for key in keys:
                valor = valor[key]
            valores.append(str(valor))
        
        # Agregar timestamp
        valores.append(str(timestamp))
        
        # Agregar events secret
        valores.append(settings.WOMPI_EVENTS_SECRET)
        
        # Concatenar todo
        cadena = ''.join(valores)
        
        # Calcular SHA256
        firma_calculada = hashlib.sha256(cadena.encode('utf-8')).hexdigest().upper()
        
        return firma_calculada == checksum_recibido.upper()
    
    @staticmethod
    def consultar_transaccion(transaction_id):
        """
        Consulta el estado de una transacción en Wompi
        """
        url = f"{WompiUtils.get_base_url()}/transactions/{transaction_id}"
        
        headers = {
            'Authorization': f'Bearer {settings.WOMPI_PUBLIC_KEY}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error consultando transacción: {e}")
            return None


def actualizar_stock_productos(detalle_pedido, usuario=None):
    """
    Actualiza el stock de las variantes de productos después de un pago exitoso.
    
    Args:
        detalle_pedido (dict): Diccionario con los productos del pedido
        usuario: Usuario que realizó la compra (opcional)
    
    Returns:
        tuple: (exitoso: bool, mensajes: list)
    """
    from carrito.models import ProductoVariante, Inventario, Producto
    from django.db import transaction
    
    mensajes = []
    exitoso = True
    
    if not detalle_pedido or 'productos' not in detalle_pedido:
        return False, ["No hay productos en el detalle del pedido"]
    
    productos = detalle_pedido.get('productos', [])
    
    # Usar transacción atómica para garantizar consistencia
    try:
        with transaction.atomic():
            for prod_data in productos:
                producto_id = prod_data.get('producto_id')
                cantidad = prod_data.get('cantidad', 0)
                talla = prod_data.get('talla')
                color = prod_data.get('color')
                nombre = prod_data.get('nombre', 'Producto')
                
                if not producto_id or cantidad <= 0:
                    mensajes.append(f"❌ Datos inválidos para producto {nombre}")
                    continue
                
                # Verificar si el producto existe
                try:
                    producto = Producto.objects.get(id=producto_id)
                except Producto.DoesNotExist:
                    mensajes.append(f"❌ Producto {nombre} (ID: {producto_id}) no encontrado")
                    exitoso = False
                    continue
                
                # Si tiene talla y color, buscar la variante
                if talla and color:
                    try:
                        variante = ProductoVariante.objects.select_for_update().get(
                            producto_id=producto_id,
                            talla=talla,
                            color=color
                        )
                        
                        # Verificar stock disponible
                        if variante.stock < cantidad:
                            mensajes.append(
                                f"⚠️ Stock insuficiente para {nombre} ({talla}/{color}). "
                                f"Disponible: {variante.stock}, Solicitado: {cantidad}"
                            )
                            exitoso = False
                            continue
                        
                        # Guardar stock anterior
                        stock_anterior = variante.stock
                        
                        # Actualizar stock
                        variante.stock -= cantidad
                        variante.save()
                        
                        # Registrar movimiento de inventario
                        Inventario.objects.create(
                            variante=variante,
                            tipo_movimiento='salida',
                            cantidad=cantidad,
                            stock_anterior=stock_anterior,
                            stock_nuevo=variante.stock,
                            usuario=usuario,
                            observaciones=f'Venta realizada - Pago Wompi'
                        )
                        
                        mensajes.append(
                            f"✅ Stock actualizado: {nombre} ({talla}/{color}) - "
                            f"Descontado: {cantidad}, Nuevo stock: {variante.stock}"
                        )
                        
                        # También actualizar el stock del producto base
                        if producto.stock >= cantidad:
                            producto.stock -= cantidad
                            producto.save()
                            mensajes.append(
                                f"✅ Stock del producto base actualizado: {nombre} - "
                                f"Nuevo stock total: {producto.stock}"
                            )
                        
                    except ProductoVariante.DoesNotExist:
                        mensajes.append(
                            f"⚠️ Variante no encontrada para {nombre} "
                            f"(Talla: {talla}, Color: {color}). Se omitirá la actualización de stock."
                        )
                        # No marcamos como error crítico ya que el pedido se creó
                        
                else:
                    # Si no tiene talla/color especificados, actualizar solo el stock general del producto
                    if producto.stock >= cantidad:
                        stock_anterior = producto.stock
                        producto.stock -= cantidad
                        producto.save()
                        mensajes.append(
                            f"✅ Stock del producto actualizado: {nombre} - "
                            f"Descontado: {cantidad}, Nuevo stock: {producto.stock}"
                        )
                    else:
                        mensajes.append(
                            f"⚠️ Stock insuficiente para {nombre}. "
                            f"Disponible: {producto.stock}, Solicitado: {cantidad}"
                        )
                        exitoso = False
        
        return exitoso, mensajes
        
    except Exception as e:
        return False, [f"❌ Error al actualizar stock: {str(e)}"]