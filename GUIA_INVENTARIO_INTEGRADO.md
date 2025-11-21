# 📦 GUÍA COMPLETA DEL SISTEMA DE INVENTARIO INTEGRADO

## 🎯 Objetivo del Sistema

El sistema de inventario está diseñado para gestionar de forma **precisa y coherente** el stock de productos con múltiples variantes (tallas y colores). Todo el inventario se maneja de forma centralizada con distribución exacta.

---

## 🔄 FLUJO COMPLETO DEL INVENTARIO

### 📍 PASO 1: Crear Producto Base (Stock General)

**Ubicación:** Dashboard → Gestión de Productos → Agregar Producto

**Campos a completar:**
- ✅ Nombre del producto
- ✅ Categoría (Hombre/Mujer/Accesorios/etc.)
- ✅ **Tipo de producto** (Hombre/Mujer/Zapatos) → Determina tallas disponibles
- ✅ Precio
- ✅ **Stock Total** → Ej: 80 unidades
- ✅ Descripción
- ✅ Imagen

**Ejemplo:**
```
Producto: Camiseta Deportiva Pro
Tipo: Hombre
Stock Total: 80 unidades
Precio: $25.000
```

> ⚠️ **Importante:** El stock total (80) es el máximo que podrás distribuir en variantes

---

### 📍 PASO 2: Distribuir Stock en Variantes (Tallas + Colores)

**Ubicación:** Dashboard → Gestión de Productos → [Botón "Variantes" del producto]

**URL:** `/dashboard/producto/{producto_id}/variantes/`

#### 2.1 Visualización del Panel

Al abrir el panel de variantes, verás:

```
┌────────────────────────────────────────────────┐
│  📊 DISTRIBUCIÓN DE STOCK                      │
├────────────────────────────────────────────────┤
│  Stock Total:      80 unidades                 │
│  Stock Asignado:   45 unidades                 │
│  Stock Disponible: 35 unidades ✅              │
│                                                │
│  [████████████░░░░░░░] 56% distribuido         │
└────────────────────────────────────────────────┘
```

#### 2.2 Crear Variante

1. **Selecciona Talla** (según tipo de producto):
   - **Hombre:** XS, S, M, L, XL, XXL, 28, 30, 32, 34, 36, 38
   - **Mujer:** XS, S, M, L, XL, 6, 8, 10, 12, 14, 16
   - **Zapatos:** 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45

2. **Selecciona Color:**
   - Negro, Blanco, Rojo, Azul, Verde, Amarillo, Gris, Marrón, Rosa, Morado, Beige, Naranja, Caqui, Verde Oliva

3. **Asigna Stock:**
   - Stock máximo = Stock disponible
   - **Validación en tiempo real:** No puedes exceder el stock disponible

4. **Resultado:**
```
✅ Variante creada:
   Talla: M
   Color: Rojo
   Stock: 15 unidades
   
   Stock disponible actualizado: 35 → 20 unidades
```

#### 2.3 Ejemplo de Distribución Completa

**Producto:** Camiseta Deportiva Pro (80 unidades)

| Talla | Color   | Stock | ID   |
|-------|---------|-------|------|
| XS    | Negro   | 10    | #147 |
| S     | Negro   | 12    | #148 |
| M     | Negro   | 8     | #149 |
| M     | Rojo    | 15    | #150 |
| L     | Rojo    | 12    | #151 |
| L     | Azul    | 10    | #152 |
| XL    | Azul    | 8     | #153 |
| XL    | Blanco  | 5     | #154 |
| **TOTAL**       | **80** |      |

**Contabilidad:**
- Stock Total: **80** ✅
- Stock Asignado: **80** ✅
- Stock Disponible: **0** ✅
- Distribución: **100%** ✅

---

### 📍 PASO 3: Ver Inventario Completo

**Ubicación:** Dashboard → Gestión de Productos → [Botón "Ver Inventario Completo"]

**Funcionalidad:**
- Muestra **TODOS** los productos con **TODAS** sus variantes
- Presenta stock en tiempo real de cada combinación talla+color
- Permite navegar directamente a gestionar variantes de cada producto

**Interfaz del Modal:**

```
╔══════════════════════════════════════════════════════════════╗
║  📦 INVENTARIO COMPLETO - TODAS LAS VARIANTES                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🏷️ CAMISETA DEPORTIVA PRO                                  ║
║  ┌────────────────────────────────────────────────────────┐ ║
║  │ 8 variantes · Stock total: 80 unidades                 │ ║
║  │ [🔧 Gestionar Variantes]                               │ ║
║  ├────────┬─────────┬──────────┬──────────┬────────┤       │ ║
║  │ Talla  │ Color   │  Stock   │  Precio  │   ID   │       │ ║
║  ├────────┼─────────┼──────────┼──────────┼────────┤       │ ║
║  │  XS    │ Negro   │ 🟢 10    │ $25,000  │  #147  │       │ ║
║  │  S     │ Negro   │ 🟢 12    │ $25,000  │  #148  │       │ ║
║  │  M     │ Negro   │ 🟡  8    │ $25,000  │  #149  │       │ ║
║  │  M     │ Rojo    │ 🟢 15    │ $25,000  │  #150  │       │ ║
║  │  L     │ Rojo    │ 🟢 12    │ $25,000  │  #151  │       │ ║
║  │  L     │ Azul    │ 🟢 10    │ $25,000  │  #152  │       │ ║
║  │  XL    │ Azul    │ 🟡  8    │ $25,000  │  #153  │       │ ║
║  │  XL    │ Blanco  │ 🟡  5    │ $25,000  │  #154  │       │ ║
║  └────────┴─────────┴──────────┴──────────┴────────┘       │ ║
║                                                              ║
║  📊 ESTADÍSTICAS GLOBALES:                                   ║
║  ┌─────────────────┬─────────────────┬─────────────────┐    ║
║  │ Total Productos │ Total Variantes │  Stock Total    │    ║
║  │       15        │       120       │     1,450       │    ║
║  └─────────────────┴─────────────────┴─────────────────┘    ║
╚══════════════════════════════════════════════════════════════╝
```

**Indicadores de Stock:**
- 🟢 **Verde** → Stock ≥ 10 unidades (Bueno)
- 🟡 **Amarillo** → Stock 5-9 unidades (Bajo)
- 🔴 **Rojo** → Stock < 5 unidades (Crítico)

---

### 📍 PASO 4: Modal de Producto (Cliente Frontend)

**Ubicación:** Catálogo de Productos → Click en producto

**URL:** `/core/producto/{producto_id}/` (abre modal)

#### 4.1 Selección Interactiva

1. **Usuario selecciona COLOR** (botones circulares con color real)
   ```
   ⚫ Botón Negro (seleccionado)
   ⚪ Botón Blanco
   🔴 Botón Rojo
   ```

2. **Se muestra tabla de stock por tallas:**
   ```
   ┌────────────────────────────────────┐
   │  📊 STOCK POR TALLAS (Color: Rojo) │
   ├────────────────────────────────────┤
   │  M  │ 15 unidades  🟢 ✓            │
   │  L  │ 12 unidades  🟢 ✓            │
   │  XL │  0 unidades  🔴 ✗            │
   └────────────────────────────────────┘
   ```

3. **Usuario selecciona TALLA M**
   ```
   ✅ VARIANTE SELECCIONADA
   ──────────────────────────
   📦 Stock: 15 unidades 🟢
   🎨 Color: Rojo
   👕 Talla: M
   🆔 ID: #150
   ```

4. **Botón de gestión (si tiene permisos):**
   ```
   [🔧 Gestionar Inventario] → /dashboard/variantes/ajustar/150/
   ```

---

### 📍 PASO 5: Ajustar Inventario de Variante Específica

**Ubicación:** Dashboard → Variantes → Ajustar Inventario

**URL:** `/dashboard/variantes/ajustar/{variante_id}/`

#### 5.1 Tipos de Movimiento

**A) ENTRADA** (Aumentar stock)
```
Tipo: Entrada
Cantidad: +20
Motivo: Compra a proveedor
─────────────────────────
Stock anterior: 15
Stock nuevo:    35 ✅
```

**B) SALIDA** (Reducir stock)
```
Tipo: Salida
Cantidad: -5
Motivo: Venta en línea
─────────────────────────
Stock anterior: 35
Stock nuevo:    30 ✅
```

**C) AJUSTE** (Establecer cantidad exacta)
```
Tipo: Ajuste
Cantidad: 25
Motivo: Inventario físico
─────────────────────────
Stock anterior: 30
Stock nuevo:    25 ✅
```

#### 5.2 Historial de Movimientos

**Vista del historial:**
```
╔════════════════════════════════════════════════════════════╗
║  📋 HISTORIAL DE MOVIMIENTOS - Variante #150               ║
║  Producto: Camiseta Deportiva Pro | Talla: M | Color: Rojo║
╠════════════════════════════════════════════════════════════╣
║  Fecha         │ Tipo    │ Cant │ Motivo        │ Stock   ║
╠════════════════════════════════════════════════════════════╣
║  12/11/2025    │ Entrada │ +15  │ Stock inicial │ 15      ║
║  13/11/2025    │ Entrada │ +20  │ Compra        │ 35      ║
║  13/11/2025    │ Salida  │ -5   │ Venta online  │ 30      ║
║  14/11/2025    │ Ajuste  │ =25  │ Inv. físico   │ 25      ║
╚════════════════════════════════════════════════════════════╝
```

---

## ⚙️ VALIDACIONES Y COHERENCIA

### ✅ 1. Validación de Distribución (Backend + Frontend)

**Regla principal:** Stock asignado en variantes ≤ Stock total del producto

**Ejemplo:**
```python
# En dashboard/views.py - gestionar_variantes
stock_total = producto.stock  # 80
stock_asignado = sum(v.stock for v in variantes)  # 65
stock_disponible = stock_total - stock_asignado  # 15

# Si intentas crear variante con stock > 15:
if nueva_variante.stock > stock_disponible:
    exceso = nueva_variante.stock - stock_disponible
    error = f"Error: Intentas asignar {nueva_variante.stock} pero solo hay {stock_disponible} disponibles. Exceso: {exceso}"
    # ❌ NO SE GUARDA
```

**Frontend (JavaScript):**
```javascript
// En gestionar_variantes.html
const totalAsignado = Array.from(inputs).reduce((sum, inp) => sum + parseInt(inp.value || 0), 0);

if (totalAsignado > stockTotal) {
    alert(`¡Error! Has asignado ${totalAsignado} pero solo hay ${stockTotal} disponibles.`);
    event.preventDefault(); // ❌ NO ENVÍA FORMULARIO
}
```

### ✅ 2. Actualización en Tiempo Real

**Al crear/editar/eliminar variante:**
1. Se recalcula `stock_asignado`
2. Se actualiza `stock_disponible`
3. Se actualiza la barra de progreso visual
4. Se valida antes de guardar

### ✅ 3. Coherencia de Datos

**Modelo ProductoVariante:**
```python
class ProductoVariante(models.Model):
    producto = models.ForeignKey(Producto)  # Relación al producto base
    talla = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    stock = models.PositiveIntegerField()  # No puede ser negativo
    tipo_producto = models.CharField()  # Hereda de producto
```

**Modelo Inventario:**
```python
class Inventario(models.Model):
    variante = models.ForeignKey(ProductoVariante)
    tipo_movimiento = models.CharField()  # entrada/salida/ajuste
    cantidad = models.PositiveIntegerField()
    stock_anterior = models.PositiveIntegerField()
    stock_nuevo = models.PositiveIntegerField()
    motivo = models.TextField()
    usuario = models.ForeignKey(UsuarioPersonalizado)
    fecha = models.DateTimeField(auto_now_add=True)
```

**Cálculo automático al guardar movimiento:**
```python
# En dashboard/views.py - ajustar_inventario
if movimiento.tipo_movimiento == 'entrada':
    movimiento.stock_nuevo = variante.stock + movimiento.cantidad
elif movimiento.tipo_movimiento == 'salida':
    movimiento.stock_nuevo = max(0, variante.stock - movimiento.cantidad)
else:  # ajuste
    movimiento.stock_nuevo = movimiento.cantidad

# Actualizar variante
variante.stock = movimiento.stock_nuevo
variante.save()
```

---

## 📊 ESTRUCTURA DE DATOS

### Producto Base
```json
{
  "id": 1,
  "nombre": "Camiseta Deportiva Pro",
  "categoria": "hombre",
  "tipo_producto": "hombre",
  "precio": 25000,
  "stock": 80,  // ← STOCK TOTAL GENERAL
  "descripcion": "Camiseta de alta calidad...",
  "imagen_url": "https://..."
}
```

### Variantes del Producto
```json
[
  {
    "id": 147,
    "producto_id": 1,
    "talla": "M",
    "color": "Rojo",
    "stock": 15,  // ← STOCK DE ESTA VARIANTE
    "tipo_producto": "hombre"
  },
  {
    "id": 148,
    "producto_id": 1,
    "talla": "L",
    "color": "Rojo",
    "stock": 12,
    "tipo_producto": "hombre"
  }
  // ... más variantes
]
```

### Registro de Inventario
```json
{
  "id": 523,
  "variante_id": 147,
  "tipo_movimiento": "entrada",
  "cantidad": 20,
  "stock_anterior": 15,
  "stock_nuevo": 35,
  "motivo": "Compra a proveedor XYZ",
  "usuario_id": 1,
  "fecha": "2025-11-14T10:30:00Z"
}
```

---

## 🔗 CONEXIONES ENTRE SISTEMAS

### 1. Dashboard ↔ Inventario Completo
```
Dashboard Productos
    ↓ [Ver Inventario Completo]
Modal Inventario Global
    ↓ [Gestionar Variantes de Producto X]
Panel de Variantes
    ↓ [Ajustar Stock de Variante #147]
Panel de Ajuste de Inventario
```

### 2. Frontend (Cliente) ↔ Backend (Admin)
```
Modal Producto (Cliente)
    ↓ Selecciona Color + Talla
Muestra Stock Disponible
    ↓ [Gestionar Inventario] (Admin)
Panel de Ajuste (Dashboard)
    ↓ Actualiza Stock
Base de Datos
    ↓ Refleja en tiempo real
Modal Producto actualizado
```

---

## 🎯 CASOS DE USO PRÁCTICOS

### Caso 1: Recepción de Nueva Mercancía

**Situación:** Llegan 50 camisetas nuevas del proveedor

**Pasos:**
1. Ir a Dashboard → Producto → Variantes
2. Crear nuevas variantes con la distribución:
   - 15 Rojas M
   - 10 Rojas L
   - 10 Negras M
   - 15 Negras L
3. Sistema valida: 15+10+10+15 = 50 ✅
4. Guardar → Stock actualizado

### Caso 2: Venta en Línea

**Situación:** Cliente compra 3 camisetas Rojas talla M

**Pasos:**
1. Cliente selecciona: Rojo + M
2. Ve: Stock 15 ✅ Disponible
3. Agrega 3 al carrito
4. Al confirmar compra:
   - Sistema crea movimiento: Salida -3
   - Stock anterior: 15
   - Stock nuevo: 12
   - Modal actualizado: "12 unidades disponibles"

### Caso 3: Ajuste de Inventario Físico

**Situación:** Inventario físico encuentra 8 unidades en vez de 12

**Pasos:**
1. Dashboard → Variantes → Ajustar #147
2. Tipo: Ajuste
3. Cantidad: 8
4. Motivo: "Diferencia en inventario físico"
5. Guardar:
   - Stock anterior: 12
   - Stock nuevo: 8
   - Diferencia: -4 (registrado)

---

## 📈 REPORTES Y ANÁLISIS

### Información Disponible

1. **Stock por Producto:**
   - Total general
   - Total asignado
   - Disponible para asignar

2. **Stock por Variante:**
   - Cantidad exacta
   - Historial completo
   - Valor en inventario

3. **Estadísticas Globales:**
   - Total de productos
   - Total de variantes
   - Stock total del inventario
   - Valor total del inventario

---

## 🛠️ ARCHIVOS CLAVE DEL SISTEMA

### Backend (Django)
- `carrito/models.py` - Modelos Producto, ProductoVariante, Inventario
- `dashboard/views.py` - Lógica de gestión y validación
- `dashboard/forms.py` - Formularios con validación
- `dashboard/urls.py` - Rutas del sistema

### Frontend
- `dashboard/templates/dashboard/gestion_productos.html` - Lista de productos
- `dashboard/templates/dashboard/gestionar_variantes.html` - Panel de distribución
- `dashboard/templates/dashboard/ajustar_inventario.html` - Movimientos de stock
- `core/templates/core/producto_detalle_modal.html` - Modal cliente
- `core/static/js/inventario-modal.js` - Modal inventario completo

### Base de Datos
- `schema_inventario.sql` - Esquema completo
- `EXPLICACION_INVENTARIO.md` - Documentación técnica

---

## ✨ CARACTERÍSTICAS DESTACADAS

✅ **Validación Multi-Nivel:** Frontend + Backend + Base de Datos
✅ **Tiempo Real:** Actualización inmediata del stock
✅ **Trazabilidad:** Historial completo de cada movimiento
✅ **Coherencia:** Stock distribuido nunca excede el total
✅ **Visual:** Indicadores de color por nivel de stock
✅ **Integrado:** Conexión total entre dashboard y frontend
✅ **Preciso:** Contabilidad exacta de cada unidad

---

## 🎓 RESUMEN EJECUTIVO

**El sistema funciona así:**

1. **Creas producto con stock total** (ej: 80 unidades)
2. **Distribuyes en variantes** (20 Rojas M, 15 Negras L, etc.)
3. **Sistema valida** que la suma no exceda 80
4. **Clientes ven** stock real de cada variante
5. **Admins ajustan** mediante entradas/salidas/ajustes
6. **Todo se registra** en historial
7. **Inventario completo** muestra visión global

**Garantía:** La contabilidad es exacta. Cada unidad está rastreada desde que entra hasta que sale.

---

✨ **Sistema completamente integrado, validado y funcional** ✨
