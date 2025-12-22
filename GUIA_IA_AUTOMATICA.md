# 🎨 GENERACIÓN AUTOMÁTICA DE IMÁGENES CON IA

## 📋 Descripción

Sistema completo para generar automáticamente imágenes recolorizadas con IA (Segment Anything Model) para variantes de productos. Funciona tanto para productos nuevos como existentes.

---

## ✨ Características

### 🔄 Generación Automática
- ✅ **Señal post_save**: Cada vez que se crea una variante sin imagen, se genera automáticamente
- ✅ **Threading**: Proceso en background para no bloquear la creación
- ✅ **Cache inteligente**: No regenera imágenes que ya existen
- ✅ **Supabase**: Todas las imágenes se suben automáticamente

### 📦 Procesamiento Masivo
- ✅ **Comando Django**: `generar_imagenes_ia` para procesar productos existentes
- ✅ **Filtros**: Por producto, color, o procesar todo
- ✅ **Modo force**: Regenerar todas las imágenes
- ✅ **Límites**: Procesar solo X variantes

---

## 🚀 Uso

### 1️⃣ Para Productos NUEVOS (Automático)

Cuando creas una nueva variante sin imagen, el sistema automáticamente:

```python
# En el dashboard, al crear variante:
variante = ProductoVariante.objects.create(
    producto=producto,
    talla='M',
    color='rojo',  # ← Sistema detecta este color
    stock=10
    # NO se asigna imagen ni imagen_url
)

# 🎨 AUTOMÁTICAMENTE:
# 1. Signal detecta que no tiene imagen
# 2. Carga imagen del producto base
# 3. Convierte "rojo" a #FF0000
# 4. Procesa con SAM + recolor
# 5. Sube a Supabase
# 6. Actualiza variante.imagen_url
# 7. Guarda en caché
```

**No necesitas hacer nada más** - la imagen se genera automáticamente en background.

---

### 2️⃣ Para Productos EXISTENTES (Comando Django)

Para procesar variantes que ya existen sin imagen:

```powershell
# Procesar TODAS las variantes sin imagen
python manage.py generar_imagenes_ia

# Procesar solo un producto específico
python manage.py generar_imagenes_ia --producto-id 45

# Procesar solo variantes de un color
python manage.py generar_imagenes_ia --color rojo

# Regenerar TODAS las imágenes (incluso las que ya tienen)
python manage.py generar_imagenes_ia --force

# Procesar solo las primeras 10 variantes
python manage.py generar_imagenes_ia --limit 10

# Combinaciones
python manage.py generar_imagenes_ia --producto-id 45 --color negro
```

**Salida del comando:**
```
🎨 Iniciando generación de imágenes con IA...
📋 Total de variantes a procesar: 15

[1/15] Procesando: Zapato Nike - 42 - Rojo (Stock: 5)
  🏷️ Categoría detectada: zapatos
  🤖 Procesando con IA (color: #FF0000)...
  ☁️ Subiendo a Supabase...
  ✅ Imagen generada exitosamente

[2/15] Procesando: Zapato Nike - 42 - Azul (Stock: 3)
  ✅ Usando imagen desde caché

============================================================
✅ RESUMEN:
  • Total procesadas: 15
  • Exitosas: 13
  • Desde caché: 2
  • Con errores: 0
============================================================
```

---

## 🎯 Cómo Funciona el Sistema

### Signal Automático (`dashboard/signals.py`)

```python
@receiver(post_save, sender=ProductoVariante)
def generar_imagen_ia_automatica(sender, instance, created, **kwargs):
    """Genera imagen automáticamente para variantes nuevas sin imagen"""
    
    # Solo si:
    if created and not instance.imagen and not instance.imagen_url:
        # 1. Cargar imagen del producto base
        # 2. Convertir color a hex
        # 3. Verificar caché
        # 4. Procesar con SAM
        # 5. Subir a Supabase
        # 6. Actualizar variante
```

### Comando de Gestión

```python
# dashboard/management/commands/generar_imagenes_ia.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Procesa variantes existentes sin imagen
        # Permite filtros y regeneración forzada
```

---

## 🎨 Conversión de Colores

El sistema convierte automáticamente nombres de colores a códigos hex:

```python
'negro'    → #000000
'blanco'   → #FFFFFF
'rojo'     → #FF0000
'azul'     → #0000FF
'verde'    → #00FF00
'amarillo' → #FFFF00
'naranja'  → #FF8000
'rosa'     → #FF69B4
'morado'   → #800080
'gris'     → #808080
'beige'    → #F5F5DC
'café'     → #8B4513
'celeste'  → #87CEEB
'turquesa' → #40E0D0
'violeta'  → #8A2BE2
```

Si usas un código hex directo (`#FF5733`), se usa tal cual.

---

## 📊 Categorías Optimizadas

El sistema detecta automáticamente la categoría del producto para aplicar configuraciones optimizadas:

| Categoría | Detección | Optimización |
|-----------|-----------|--------------|
| **Zapatos** | `producto.categoria == 'zapatos'` | Saturación alta, brillo +28% |
| **Ropa** | `categoria in ['mujer', 'hombre']` | Balance saturation/brillo |
| **Accesorios** | Palabras clave: gafas, bufanda, cinturón | Saturación máxima |
| **Bolsos** | Palabras clave: bolso, mochila, cartera | Configuración intermedia |
| **General** | Por defecto | Configuración estándar |

---

## 💾 Sistema de Caché

Para evitar regenerar la misma imagen:

```python
# Modelo ImagenColorCache
variante + color_hex → imagen_url

# Ejemplo:
Zapato Nike #42 + #FF0000 → https://supabase.co/.../rojo.png
```

**Ventajas:**
- ⚡ Respuesta instantánea si ya existe
- 💰 Ahorro de procesamiento IA
- 🔄 Reutilización entre variantes del mismo producto

---

## 🔧 Configuración Requerida

### 1. Variables de Entorno

```powershell
# En PowerShell
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
$env:SAM_MODEL_TYPE = 'vit_h'

# Permanente (reiniciar terminal después)
[System.Environment]::SetEnvironmentVariable('SAM_CHECKPOINT', 'C:\models\sam_vit_h.pth', 'User')
[System.Environment]::SetEnvironmentVariable('SAM_MODEL_TYPE', 'vit_h', 'User')
```

### 2. Modelo SAM Descargado

```powershell
# Opción A: Script automático
.\setup_sam_recolor.ps1

# Opción B: Manual
New-Item -ItemType Directory -Force -Path C:\models
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth" -OutFile "C:\models\sam_vit_h.pth"
```

### 3. Dependencias Python

```powershell
pip install torch torchvision opencv-python pillow numpy
pip install git+https://github.com/facebookresearch/segment-anything.git
```

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Tienda de Zapatos

```python
# Crear producto base
zapato = Producto.objects.create(
    nombre="Nike Air Max",
    categoria='zapatos',
    precio=150000,
    imagen_url="https://ejemplo.com/nike-blanco.jpg"
)

# Crear variantes - imágenes se generan AUTOMÁTICAMENTE
variantes_colores = ['rojo', 'azul', 'negro', 'blanco']
for color in variantes_colores:
    for talla in [38, 40, 42, 44]:
        ProductoVariante.objects.create(
            producto=zapato,
            talla=str(talla),
            color=color,
            stock=10
        )
        # ✨ Imagen generada automáticamente en background

# Resultado: 16 variantes con imágenes únicas generadas por IA
```

### Ejemplo 2: Procesar Inventario Existente

```powershell
# Tienes 500 variantes sin imagen
python manage.py generar_imagenes_ia

# Procesar solo zapatos (producto 45-60)
for ($i=45; $i -le 60; $i++) {
    python manage.py generar_imagenes_ia --producto-id $i
}

# Procesar solo 50 variantes para probar
python manage.py generar_imagenes_ia --limit 50
```

### Ejemplo 3: Actualizar Todas las Imágenes

```powershell
# Regenerar TODAS las imágenes con configuración mejorada
python manage.py generar_imagenes_ia --force

# ⚠️ ADVERTENCIA: Esto regenera TODAS las variantes
# Usa solo si cambiaste la configuración de SAM
```

---

## 🐛 Solución de Problemas

### ❌ "SAM no disponible: Checkpoint SAM no encontrado"

```powershell
# Verificar variable
echo $env:SAM_CHECKPOINT

# Debe mostrar: C:\models\sam_vit_h.pth
# Si no aparece, definir:
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'

# Verificar archivo existe
Test-Path $env:SAM_CHECKPOINT
# Debe devolver: True
```

### ❌ "segment-anything no está instalado"

```powershell
pip install git+https://github.com/facebookresearch/segment-anything.git
```

### ❌ Procesamiento muy lento

**Soluciones:**

1. **Usar GPU** (si tienes NVIDIA):
```powershell
nvidia-smi  # Verificar GPU
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

2. **Usar modelo más ligero**:
```powershell
# Descargar vit_b (375MB, más rápido)
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth" -OutFile "C:\models\sam_vit_b.pth"

# Cambiar variables
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_b.pth'
$env:SAM_MODEL_TYPE = 'vit_b'
```

3. **Procesar por lotes**:
```powershell
# En vez de todo a la vez
python manage.py generar_imagenes_ia --limit 20
# Repetir varias veces
```

### ⚠️ "Producto sin imagen base, saltando"

**Causa:** El producto no tiene `imagen` ni `imagen_url`.

**Solución:**
```python
# Asignar imagen al producto base primero
producto = Producto.objects.get(id=45)
producto.imagen_url = "https://ejemplo.com/imagen.jpg"
producto.save()

# Ahora procesar variantes
python manage.py generar_imagenes_ia --producto-id 45
```

---

## 📊 Estadísticas y Monitoreo

### Ver Caché de Imágenes

```python
from dashboard.models import ImagenColorCache

# Total de imágenes en caché
ImagenColorCache.objects.count()

# Por producto
producto = Producto.objects.get(id=45)
variantes_ids = producto.variantes.values_list('id', flat=True)
ImagenColorCache.objects.filter(variante_id__in=variantes_ids).count()

# Limpiar caché antiguo (opcional)
from datetime import timedelta
from django.utils import timezone
fecha_limite = timezone.now() - timedelta(days=30)
ImagenColorCache.objects.filter(fecha_generacion__lt=fecha_limite).delete()
```

### Ver Variantes sin Imagen

```python
from carrito.models import ProductoVariante

# Total sin imagen
ProductoVariante.objects.filter(
    imagen='', 
    imagen_url__isnull=True
).count()

# Por producto
Producto.objects.annotate(
    sin_imagen=Count('variantes', filter=Q(
        variantes__imagen='',
        variantes__imagen_url__isnull=True
    ))
).filter(sin_imagen__gt=0)
```

---

## 🎯 Mejores Prácticas

### ✅ DO's

1. **Usa imágenes de alta calidad** como base (min 1024x1024)
2. **Define colores en hex** cuando sea posible (`#FF0000` vs `"rojo"`)
3. **Asigna categoría correcta** al producto para mejor calidad
4. **Procesa en lotes** si tienes muchas variantes (--limit 50)
5. **Verifica caché** antes de regenerar (`ImagenColorCache`)

### ❌ DON'Ts

1. **No uses --force** a menos que sea necesario (gasta recursos)
2. **No proceses sin SAM configurado** (revisa `$env:SAM_CHECKPOINT`)
3. **No uses imágenes muy pequeñas** (<512x512) - calidad baja
4. **No ignores errores** - revisa logs si algo falla
5. **No crees variantes sin producto base** con imagen

---

## 🔗 Referencias

- **Documentación completa**: `SISTEMA_RECOLORIZACION_IA.md`
- **Quick Start**: `README_RECOLORIZACION.md`
- **Comandos rápidos**: `COMANDOS_RAPIDOS.md`
- **Signal**: `dashboard/signals.py` (línea ~112)
- **Comando**: `dashboard/management/commands/generar_imagenes_ia.py`
- **Vista API**: `dashboard/views.py::generar_imagen_color`

---

## 📞 Soporte

Si tienes problemas:

1. Verifica configuración: `echo $env:SAM_CHECKPOINT`
2. Verifica modelo descargado: `Test-Path $env:SAM_CHECKPOINT`
3. Prueba con una variante: `python manage.py generar_imagenes_ia --limit 1`
4. Revisa logs del servidor Django
5. Verifica imágenes en Supabase Storage

---

## ✅ Checklist de Validación

- [ ] SAM_CHECKPOINT definido y archivo existe
- [ ] SAM_MODEL_TYPE definido (vit_h, vit_l, o vit_b)
- [ ] segment-anything instalado (`pip list | Select-String segment`)
- [ ] Productos tienen imagen base (imagen o imagen_url)
- [ ] Supabase configurado correctamente
- [ ] Signal activo en `dashboard/signals.py`
- [ ] Comando disponible: `python manage.py help generar_imagenes_ia`

---

**¡El sistema está listo para generar imágenes automáticamente para todos tus productos! 🎨✨**
