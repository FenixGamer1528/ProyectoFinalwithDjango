# 📦 Sistema de Gestión de Stock con Wompi

## Descripción General

Este sistema integra automáticamente la actualización de stock de productos con variantes (talla y color) cuando se realiza un pago exitoso a través de la pasarela de pago Wompi.

## 🔄 Flujo de Trabajo

### 1. Usuario Agrega Productos al Carrito
- El usuario selecciona un producto, talla y color
- Se crea un `ItemCarrito` que almacena:
  - Producto
  - Talla seleccionada
  - Color seleccionado
  - Cantidad

### 2. Usuario Procede al Pago
- Se ejecuta `checkout_desde_carrito()`
- Se genera una transacción en Wompi con:
  - Detalle completo de productos (ID, nombre, precio, cantidad, talla, color)
  - Referencia única
  - Firma de integridad

### 3. Pago Procesado por Wompi
El pago puede confirmarse de dos formas:

#### A. Webhook (Recomendado)
```python
@csrf_exempt
def webhook_wompi(request):
    # Wompi envía notificación automática
    # Se verifica la firma de seguridad
    # Si el pago es APPROVED:
    #   1. Se crean los pedidos
    #   2. Se actualiza el stock (actualizar_stock_productos)
    #   3. Se vacía el carrito
```

#### B. Confirmación desde Frontend
```python
def confirmar_pago_carrito(request):
    # Usuario es redirigido de vuelta después del pago
    # Se consulta el estado en Wompi
    # Si el pago es APPROVED:
    #   1. Se crean los pedidos
    #   2. Se actualiza el stock (actualizar_stock_productos)
    #   3. Se vacía el carrito
```

### 4. Actualización Automática de Stock

La función `actualizar_stock_productos()` en `pagos/utils.py` realiza:

```python
def actualizar_stock_productos(detalle_pedido, usuario=None):
    """
    Para cada producto en el pedido:
    1. Busca la variante (producto + talla + color)
    2. Verifica stock disponible
    3. Descuenta la cantidad vendida
    4. Registra el movimiento en el Inventario
    """
```

#### Pasos Detallados:

1. **Búsqueda de Variante**
   ```python
   variante = ProductoVariante.objects.get(
       producto_id=producto_id,
       talla=talla,
       color=color
   )
   ```

2. **Verificación de Stock**
   ```python
   if variante.stock < cantidad:
       # Rechaza la operación
       # Registra advertencia
   ```

3. **Actualización Atómica**
   ```python
   with transaction.atomic():
       stock_anterior = variante.stock
       variante.stock -= cantidad
       variante.save()
   ```

4. **Registro de Movimiento**
   ```python
   Inventario.objects.create(
       variante=variante,
       tipo_movimiento='salida',
       cantidad=cantidad,
       stock_anterior=stock_anterior,
       stock_nuevo=variante.stock,
       usuario=usuario,
       observaciones='Venta realizada - Pago Wompi'
   )
   ```

## 📊 Modelos Involucrados

### ItemCarrito
```python
class ItemCarrito(models.Model):
    carrito = ForeignKey(Carrito)
    producto = ForeignKey(Producto)
    talla = CharField(max_length=20)      # ✅ NUEVO
    color = CharField(max_length=50)      # ✅ NUEVO
    cantidad = PositiveIntegerField()
```

### ProductoVariante
```python
class ProductoVariante(models.Model):
    producto = ForeignKey(Producto)
    talla = CharField(max_length=10)
    color = CharField(max_length=50)
    stock = IntegerField()                # Se actualiza automáticamente
    # unique_together = ['producto', 'talla', 'color']
```

### Inventario
```python
class Inventario(models.Model):
    variante = ForeignKey(ProductoVariante)
    tipo_movimiento = CharField()         # 'entrada', 'salida', 'ajuste'
    cantidad = IntegerField()
    stock_anterior = IntegerField()
    stock_nuevo = IntegerField()
    fecha = DateTimeField()
    usuario = ForeignKey(User)
    observaciones = TextField()
```

### Transaccion
```python
class Transaccion(models.Model):
    usuario = ForeignKey(User)
    referencia = CharField(unique=True)
    monto = DecimalField()
    estado = CharField()                  # PENDING, APPROVED, DECLINED
    detalle_pedido = JSONField()          # ✅ Contiene productos con talla y color
    # {
    #   'productos': [
    #     {
    #       'producto_id': 1,
    #       'nombre': 'Camisa',
    #       'precio': 50000,
    #       'cantidad': 2,
    #       'talla': 'M',
    #       'color': 'Azul'
    #     }
    #   ]
    # }
```

## 🔒 Seguridad y Consistencia

### Transacciones Atómicas
```python
with transaction.atomic():
    # Todas las operaciones se completan o ninguna
    # Previene inconsistencias si hay errores
```

### Select For Update
```python
variante = ProductoVariante.objects.select_for_update().get(...)
# Bloquea el registro hasta que termine la transacción
# Previene condiciones de carrera
```

### Verificación de Stock
```python
if variante.stock < cantidad:
    # Se registra advertencia
    # No se permite venta sin stock
    exitoso = False
```

## 📝 Registro de Actividad

Cada movimiento de stock queda registrado en la tabla `Inventario`:

```
| Variante        | Tipo    | Cantidad | Stock Ant. | Stock Nuevo | Usuario | Observaciones           |
|-----------------|---------|----------|------------|-------------|---------|-------------------------|
| Camisa M Azul   | salida  | 2        | 50         | 48          | user123 | Venta - Pago Wompi      |
| Pantalón 32 Neg | salida  | 1        | 20         | 19          | user456 | Venta - Pago Wompi      |
```

## 🎯 Casos de Uso

### ✅ Caso Exitoso
1. Usuario compra 2 camisas M Azul (stock: 50)
2. Pago aprobado en Wompi
3. Stock actualizado: 48
4. Movimiento registrado en Inventario
5. Carrito vaciado

### ⚠️ Stock Insuficiente
1. Usuario intenta comprar 10 zapatos 38 Negro (stock: 5)
2. Pago procesado en Wompi
3. Pedido creado pero stock NO se descuenta
4. Se registra advertencia en logs
5. Administrador debe resolver manualmente

### 🔍 Variante No Existe
1. Usuario compra producto sin variante configurada
2. Pago aprobado
3. Pedido creado
4. Se registra advertencia: "Variante no encontrada"
5. Stock no se actualiza (requiere revisión manual)

## 🛠️ Configuración Necesaria

### 1. Variables de Entorno
```python
# settings.py
WOMPI_PUBLIC_KEY = 'pub_test_xxxxx'
WOMPI_PRIVATE_KEY = 'prv_test_xxxxx'
WOMPI_INTEGRITY_SECRET = 'test_integrity_xxxxx'
WOMPI_EVENTS_SECRET = 'test_events_xxxxx'
WOMPI_ENV = 'TEST'  # o 'PROD'
```

### 2. URLs Configuradas
```python
# urls.py
path('webhook/', webhook_wompi, name='webhook_wompi'),
path('confirmacion-carrito/', confirmar_pago_carrito, name='confirmacion_carrito'),
```

### 3. Webhook en Wompi
- Configurar en panel de Wompi: `https://tudominio.com/pagos/webhook/`
- Validar que eventos `transaction.updated` estén activados

## 📈 Monitoreo

### Logs a Revisar
```python
print("✅ Stock actualizado: Camisa M Azul - Descontado: 2, Nuevo stock: 48")
print("⚠️ Stock insuficiente para Zapatos 38 Negro. Disponible: 5, Solicitado: 10")
print("⚠️ Variante no encontrada para Pantalón (Talla: 32, Color: Gris)")
```

### Consultas Útiles
```python
# Ver movimientos recientes
Inventario.objects.filter(tipo_movimiento='salida').order_by('-fecha')[:10]

# Ver stock bajo
ProductoVariante.objects.filter(stock__lt=10)

# Ver transacciones aprobadas sin stock actualizado
# (revisar logs para detectar estos casos)
```

## 🚀 Próximas Mejoras

1. **Notificaciones**: Enviar email cuando stock esté bajo
2. **Reserva temporal**: Reservar stock al crear orden, confirmar al pagar
3. **Reintegro**: Devolver stock si pago es rechazado o pedido cancelado
4. **Dashboard**: Gráficas de movimientos de inventario
5. **Alertas**: Notificar administrador cuando no haya stock suficiente

## 🐛 Resolución de Problemas

### Stock no se actualiza
- ✅ Verificar que `talla` y `color` estén en `detalle_pedido`
- ✅ Verificar que la variante existe en la base de datos
- ✅ Revisar logs de la función `actualizar_stock_productos`

### Error en webhook
- ✅ Verificar firma de integridad
- ✅ Verificar que `WOMPI_EVENTS_SECRET` esté configurado
- ✅ Revisar logs del servidor para el endpoint `/pagos/webhook/`

### Descuento doble
- ✅ El sistema previene esto con transacciones atómicas
- ✅ Webhook y confirmación frontend usan la misma lógica
- ✅ Estado de transacción evita duplicados

---

**Fecha de Implementación**: Diciembre 2025  
**Versión**: 1.0  
**Desarrollador**: FenixGamer1528
