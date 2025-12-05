# 🚀 Guía Rápida: Stock Automático con Wompi

## ✅ ¿Qué se implementó?

Ahora cuando un usuario compra un producto a través de Wompi, el stock se actualiza automáticamente:

- ✅ Se descuenta el stock de la variante específica (talla + color)
- ✅ Se registra el movimiento en el historial de inventario
- ✅ Se previenen ventas sin stock suficiente
- ✅ Se maneja con transacciones atómicas (seguro)

## 📋 Cambios Realizados

### 1. Modelo ItemCarrito
**Archivo**: `carrito/models.py`

```python
class ItemCarrito(models.Model):
    # ... campos existentes ...
    talla = CharField(max_length=20)
    color = CharField(max_length=50)  # ✅ NUEVO
    cantidad = PositiveIntegerField()
```

**Migración aplicada**: `0004_itemcarrito_color.py`

### 2. Función de Actualización de Stock
**Archivo**: `pagos/utils.py`

Nueva función `actualizar_stock_productos()`:
- Busca la variante (producto + talla + color)
- Verifica stock disponible
- Descuenta la cantidad vendida
- Registra movimiento en Inventario
- Usa transacciones atómicas

### 3. Webhook de Wompi
**Archivo**: `pagos/views.py` → `webhook_wompi()`

```python
if datos_transaccion['status'] == 'APPROVED':
    # ... crear pedidos ...
    
    # ✅ NUEVO: Actualizar stock
    exitoso, mensajes = actualizar_stock_productos(
        transaccion.detalle_pedido,
        transaccion.usuario
    )
```

### 4. Confirmación de Pago Frontend
**Archivo**: `pagos/views.py` → `confirmar_pago_carrito()`

```python
if datos_wompi['data']['status'] == 'APPROVED':
    # ... crear pedidos ...
    
    # ✅ NUEVO: Actualizar stock
    exitoso, mensajes = actualizar_stock_productos(
        transaccion.detalle_pedido,
        transaccion.usuario
    )
```

### 5. Checkout desde Carrito
**Archivo**: `pagos/views.py` → `checkout_desde_carrito()`

```python
detalle_productos.append({
    'producto_id': item.producto.id,
    'nombre': item.producto.nombre,
    'precio': float(item.producto.precio),
    'cantidad': item.cantidad,
    'talla': item.talla,
    'color': item.color,  # ✅ NUEVO
    'subtotal': float(item.subtotal())
})
```

## 🧪 Pruebas Realizadas

Ejecutar: `python test_stock_wompi.py`

Resultados:
- ✅ Creación de variantes: OK
- ✅ Actualización de stock: OK
- ✅ Registro de movimientos: OK
- ✅ Stock insuficiente: DETECTADO correctamente
- ✅ Variante inexistente: MANEJADO correctamente

## 📊 Cómo Usar el Sistema

### Paso 1: Crear Variantes de Productos

Desde el admin de Django o mediante código:

```python
from carrito.models import Producto, ProductoVariante

producto = Producto.objects.get(id=1)

# Crear variantes
ProductoVariante.objects.create(
    producto=producto,
    talla='M',
    color='Azul',
    stock=50,
    tipo_producto='ropa'
)
```

### Paso 2: Usuario Agrega al Carrito

El frontend debe enviar talla y color al agregar al carrito:

```python
# En views.py de carrito
item = ItemCarrito.objects.create(
    carrito=carrito,
    producto=producto,
    talla=request.POST.get('talla'),
    color=request.POST.get('color'),  # ✅ NUEVO
    cantidad=cantidad
)
```

### Paso 3: Usuario Paga con Wompi

El proceso es automático:
1. Usuario hace checkout → se crea transacción con detalle
2. Wompi procesa el pago
3. Si aprobado → se actualiza stock automáticamente
4. Se registra movimiento en Inventario

### Paso 4: Ver Movimientos de Inventario

```python
from carrito.models import Inventario

# Ver últimos movimientos
movimientos = Inventario.objects.all().order_by('-fecha')[:10]

for mov in movimientos:
    print(f"{mov.variante} - {mov.tipo_movimiento} - {mov.cantidad} unidades")
```

## 🔍 Verificar Stock

### Desde Admin de Django
1. Ir a: Carrito → Producto variantes
2. Ver stock de cada combinación talla/color
3. Ver movimientos en: Carrito → Inventarios

### Desde Código
```python
from carrito.models import ProductoVariante

# Ver stock de una variante específica
variante = ProductoVariante.objects.get(
    producto__nombre='Camisa',
    talla='M',
    color='Azul'
)
print(f"Stock: {variante.stock}")

# Ver variantes con stock bajo
bajo_stock = ProductoVariante.objects.filter(stock__lt=10)
```

## ⚠️ Casos Especiales

### Stock Insuficiente
- El sistema detecta cuando no hay suficiente stock
- El pedido se crea pero el stock NO se descuenta
- Se registra advertencia en los logs
- El administrador debe resolver manualmente

### Variante No Existe
- Si el usuario intenta comprar una combinación talla/color que no existe
- El pedido se crea pero el stock NO se descuenta
- Se registra advertencia en los logs
- Solución: Crear la variante faltante

### Producto Sin Variantes
- Si el producto no tiene talla/color configurados
- El pedido se crea normalmente
- No se actualiza stock de variantes (porque no existen)
- Puedes usar el campo `Producto.stock` para control general

## 🛠️ Comandos Útiles

### Crear Migración (ya aplicada)
```bash
python manage.py makemigrations carrito
python manage.py migrate carrito
```

### Probar Sistema
```bash
python test_stock_wompi.py
```

### Ver Logs del Servidor
```bash
# En tu servidor, ver logs cuando procese pagos
tail -f logs/django.log
```

## 📱 Frontend

El frontend debe capturar talla y color al agregar al carrito:

```html
<form method="POST" action="{% url 'agregar_carrito' producto.id %}">
    {% csrf_token %}
    
    <select name="talla" required>
        <option value="">Selecciona talla</option>
        <option value="S">S</option>
        <option value="M">M</option>
        <option value="L">L</option>
    </select>
    
    <select name="color" required>
        <option value="">Selecciona color</option>
        <option value="Rojo">Rojo</option>
        <option value="Azul">Azul</option>
        <option value="Negro">Negro</option>
    </select>
    
    <input type="number" name="cantidad" value="1" min="1">
    
    <button type="submit">Agregar al Carrito</button>
</form>
```

## 🎯 Próximos Pasos Recomendados

1. **Actualizar vistas de carrito** para mostrar talla y color
2. **Validar stock antes del checkout** (frontend)
3. **Notificaciones** cuando stock esté bajo
4. **Dashboard de inventario** con gráficas
5. **API para consultar stock** en tiempo real

## 📚 Documentación Completa

Ver: `GUIA_STOCK_WOMPI.md` para documentación detallada

---

**¿Preguntas?** Revisa los logs o ejecuta `python test_stock_wompi.py`
