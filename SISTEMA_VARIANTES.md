# Sistema de Gestión de Productos con Variantes

## ✅ Funcionalidades Implementadas

### 1️⃣ Tallas Dinámicas por Tipo de Producto
- **ROPA**: XS, S, M, L, XL, XXL
- **PANTALONES**: 28, 30, 32, 34, 36, 38, 40
- **ZAPATOS**: 36, 37, 38, 39, 40, 41, 42, 43, 44

### 2️⃣ Colores por Tipo de Producto
- **ROPA**: Blanco, Negro, Rojo, Azul, Verde, Amarillo, Gris, Marrón, Rosa, Morado
- **PANTALONES**: Negro, Azul, Gris, Marrón, Caqui
- **ZAPATOS**: Negro, Blanco, Marrón, Beige, Azul, Rojo

### 3️⃣ Sistema de Variantes
- Cada producto puede tener múltiples variantes (combinaciones de talla + color)
- Cada variante tiene:
  - Talla específica
  - Color específico
  - Stock independiente
  - Imagen propia (opcional)
  - Indicador si fue generada por IA

### 4️⃣ Inventario por Variante
- **Registro de movimientos**: Entradas, Salidas, Ajustes
- **Historial completo** con:
  - Fecha y hora
  - Usuario que realizó el movimiento
  - Stock anterior y nuevo
  - Observaciones
- **Control de stock** en tiempo real por cada variante

### 5️⃣ Página de Detalle de Producto
- **Selección interactiva** de talla y color
- **Cambio automático de imagen** según variante seleccionada
- **Stock en tiempo real** para la combinación elegida
- **Deshabilita opciones** sin stock disponible
- **Botón de favoritos** integrado
- **Agregar al carrito** con validación de stock

---

## 🚀 Cómo Usar el Sistema

### Para Administradores (Dashboard)

#### 1. Crear un Producto Base
1. Ve a **Dashboard → Gestión de Productos**
2. Haz clic en **Agregar Producto**
3. Completa los datos básicos:
   - Nombre
   - Categoría
   - Precio
   - Descripción
   - Imagen principal
   - Stock (este se reemplazará por las variantes)

#### 2. Agregar Variantes al Producto
1. En la lista de productos, haz clic en **Variantes** del producto creado
2. Selecciona el **Tipo de Producto** (Ropa, Pantalones o Zapatos)
3. Las tallas y colores se cargarán automáticamente
4. Selecciona **Talla**
5. Selecciona **Color**
6. Ingresa el **Stock Inicial**
7. Opcionalmente sube una **Imagen** específica para esta variante
8. Haz clic en **Crear Variante**

#### 3. Gestionar Inventario
1. Desde la página de **Variantes**, haz clic en **Ajustar** en la variante deseada
2. Selecciona el tipo de movimiento:
   - **Entrada**: Suma stock (ej: nueva compra)
   - **Salida**: Resta stock (ej: venta, devolución)
   - **Ajuste**: Establece stock exacto (ej: inventario físico)
3. Ingresa la cantidad
4. Agrega observaciones (opcional)
5. Guarda el movimiento

#### 4. Ver Historial de Inventario
- Haz clic en **Historial** en cualquier variante
- Verás todos los movimientos con fechas, usuarios y cambios

### Para Clientes (Frontend)

#### 1. Ver Detalles del Producto
- Haz clic en cualquier producto de la tienda
- Se abrirá la página de detalle con todas las variantes

#### 2. Seleccionar Variante
1. Elige una **Talla** (las opciones sin stock estarán deshabilitadas)
2. Elige un **Color** (las opciones sin stock estarán deshabilitadas)
3. La imagen cambiará automáticamente
4. Verás el **stock disponible** para esa combinación

#### 3. Agregar al Carrito
- Una vez seleccionada talla y color, el botón **Agregar al Carrito** se habilitará
- Haz clic para agregar el producto

---

## 🤖 Integración de IA para Cambio de Color (OPCIONAL)

### Opciones de API Recomendadas

#### **Opción 1: Replicate (Recomendado)**
**API**: Stable Diffusion ControlNet

```python
# Instalar SDK
pip install replicate

# En dashboard/views.py, función generar_imagen_color()
import replicate

def generar_imagen_color(request, variante_id):
    variante = get_object_or_404(ProductoVariante, id=variante_id)
    imagen_original = variante.producto.imagen_url
    
    output = replicate.run(
        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        input={
            "image": imagen_original,
            "prompt": f"Product photo with {variante.color} color, maintain original texture, professional lighting",
            "negative_prompt": "blur, low quality, deformed",
            "guidance_scale": 7.5
        }
    )
    
    # Guardar imagen generada
    variante.imagen_url = output[0]
    variante.imagen_generada_ia = True
    variante.save()
    
    return JsonResponse({'success': True, 'imagen_url': variante.imagen_url})
```

**Costo**: ~$0.002 por imagen
**Enlace**: https://replicate.com/

---

#### **Opción 2: OpenAI DALL-E**
```python
import openai

openai.api_key = 'tu-api-key'

response = openai.Image.create_edit(
    image=open("imagen_original.png", "rb"),
    prompt=f"Change the color to {variante.color}",
    n=1,
    size="1024x1024"
)

imagen_url = response['data'][0]['url']
```

**Costo**: ~$0.02 por imagen
**Enlace**: https://platform.openai.com/

---

#### **Opción 3: Runway ML**
**API**: Gen-2 Video/Image

**Costo**: Desde $15/mes
**Enlace**: https://runwayml.com/

---

#### **Opción 4: Cloudinary AI Background Removal + Color Overlay**
```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name = "tu-cloud-name",
    api_key = "tu-api-key",
    api_secret = "tu-api-secret"
)

# Subir y procesar
result = cloudinary.uploader.upload(
    imagen_original,
    transformation=[
        {'effect': 'recolor', 'color': variante.color}
    ]
)

imagen_url = result['secure_url']
```

**Costo**: Gratis hasta 25 créditos/mes
**Enlace**: https://cloudinary.com/

---

### Configuración Recomendada

**Archivo**: `glamoure/settings.py`

```python
# Configuración de API para IA
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')
```

**Archivo**: `.env` (crear en raíz del proyecto)
```
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrst
```

---

## 📋 Rutas Disponibles

### Dashboard (Administradores)
- `/dashboard/producto/<id>/variantes/` - Gestionar variantes de un producto
- `/dashboard/variante/<id>/editar/` - Editar variante
- `/dashboard/variante/<id>/eliminar/` - Eliminar variante
- `/dashboard/variante/<id>/inventario/` - Ver historial de inventario
- `/dashboard/variante/<id>/ajustar/` - Ajustar stock (entrada/salida/ajuste)

### Frontend (Clientes)
- `/producto/<id>/` - Ver detalle del producto con variantes

### APIs
- `/dashboard/api/producto/<id>/variantes/` - Obtener variantes de un producto (JSON)
- `/dashboard/api/variante/<id>/generar-color/` - Generar imagen con IA (pendiente integración)

---

## 🗄️ Modelos Creados

### `ProductoVariante`
```python
producto (FK)
tipo_producto (ropa/pantalones/zapatos)
talla (CharField)
color (CharField)
stock (IntegerField)
imagen (ImageField)
imagen_url (URLField)
imagen_generada_ia (BooleanField)
```

### `Inventario`
```python
variante (FK)
tipo_movimiento (entrada/salida/ajuste)
cantidad (IntegerField)
stock_anterior (IntegerField)
stock_nuevo (IntegerField)
fecha (DateTimeField)
usuario (FK)
observaciones (TextField)
```

---

## 🧪 Pruebas Recomendadas

### 1. Crear un Producto con Variantes
```bash
1. Crea un producto "Buzo Deportivo" en Dashboard
2. Agrega variantes:
   - Buzo Negro M (stock: 10)
   - Buzo Negro L (stock: 5)
   - Buzo Rojo M (stock: 8)
   - Buzo Rojo L (stock: 0)
```

### 2. Probar Página de Detalle
```bash
1. Ve a /producto/<id>/
2. Selecciona talla M y color Negro → Debe mostrar stock 10
3. Selecciona talla L y color Rojo → Botón deshabilitado (stock 0)
4. Cambia a color Negro → Imagen debe cambiar
```

### 3. Probar Inventario
```bash
1. Desde variantes, haz clic en "Ajustar" en Buzo Negro M
2. Registra entrada de 5 unidades
3. Ve al historial → Debe mostrar stock anterior: 10, stock nuevo: 15
4. Verifica que el stock se actualizó en la variante
```

---

## 📦 Migraciones Aplicadas

```bash
python manage.py makemigrations
python manage.py migrate
```

**Migraciones creadas**:
- `0010_add_colores.py` - Añade campo colores a Producto
- `0011_merge_*.py` - Merge de ramas de migración
- `0012_producto_talla_productovariante_inventario_and_more.py` - Crea variantes e inventario

---

## 🎨 Estilos Aplicados

Todos los templates siguen el estilo de la página:
- **Fondo negro** (#000000)
- **Color dorado** (#C0A76B) para elementos destacados
- **Borders y hover** con transiciones suaves
- **Font Awesome icons** para mejor UX
- **Tailwind CSS** para diseño responsive

---

## ⚠️ Notas Importantes

1. **Stock del producto base** vs **Stock de variantes**:
   - El campo `Producto.stock` es legacy y se mantiene por compatibilidad
   - El stock real se gestiona en las variantes (`ProductoVariante.stock`)

2. **Imágenes**:
   - Cada variante puede tener su propia imagen
   - Si no tiene, se muestra la imagen del producto base
   - La IA puede generar imágenes automáticamente (requiere integración)

3. **Carrito**:
   - Al agregar al carrito, se debe especificar la talla seleccionada
   - El sistema de carrito existente ya soporta tallas (`ItemCarrito.talla`)

4. **Migración de datos**:
   - Si ya tienes productos, necesitarás crear variantes manualmente
   - O crear un script de migración para generar variantes automáticamente

---

## 🔧 Próximos Pasos (Opcional)

1. **Integrar API de IA** para cambio de color automático
2. **Script de migración** de datos existentes a variantes
3. **Reportes de inventario** (productos más vendidos, bajo stock, etc.)
4. **Alertas de stock bajo** (notificaciones automáticas)
5. **Importación/exportación** de inventario (CSV/Excel)
6. **Búsqueda y filtros** por talla y color en la tienda
7. **Imágenes múltiples** por variante (galería)

---

## 📞 Soporte

Si necesitas ayuda con la integración de IA o tienes dudas sobre el sistema, revisa la documentación de las APIs mencionadas o consulta con el equipo de desarrollo.
