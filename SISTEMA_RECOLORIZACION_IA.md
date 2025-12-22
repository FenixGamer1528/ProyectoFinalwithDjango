# Sistema de Recolorización de Imágenes con IA (SAM)

## 📋 Descripción General

Sistema integrado en Django para cambiar automáticamente el color de productos (ropa, zapatos, etc.) usando **Segment Anything Model (SAM)** de Meta + recolorización HSV. Permite generar múltiples variantes de color sin necesidad de fotografiar cada prenda en cada color.

## 🎯 Características

- ✅ **Segmentación automática** con SAM (detecta automáticamente el objeto principal)
- ✅ **Recolorización preservando textura** (solo cambia tono, mantiene sombras/luces)
- ✅ **Integración con Django** y API REST lista para usar
- ✅ **Subida automática a Supabase** de imágenes procesadas
- ✅ **Soporta múltiples fuentes**: imagen subida POST, imagen de variante o producto base
- ✅ **Preview en base64** para visualización inmediata
- ✅ **Marcado automático** de imágenes generadas por IA

---

## 🏗️ Arquitectura

### Componentes

```
dashboard/
├── sam_recolor.py          # Módulo de procesamiento SAM + recolor
├── views.py                # Vista API generar_imagen_color
└── urls.py                 # Ruta: /api/variante/<id>/generar-color/

carrito/
└── models.py               # ProductoVariante (imagen_url, imagen_generada_ia)

core/utils/
└── supabase_storage.py     # Subida de imágenes a Supabase
```

### Flujo de Procesamiento

```
1. Cliente → POST /api/variante/<id>/generar-color/
            ├─ image: archivo (opcional)
            └─ color: hex ej. #ff0000

2. Django → Cargar imagen
            ├─ Prioridad 1: archivo POST
            ├─ Prioridad 2: variante.imagen/imagen_url
            └─ Prioridad 3: producto.imagen/imagen_url

3. SAM → Generar máscara automática (detecta objeto principal)

4. Recolor HSV → Cambiar color preservando textura
                 └─ Calcula desplazamiento de tono (Hue)

5. Supabase → Subir imagen resultante
               └─ Actualizar variante.imagen_url

6. Response → JSON con:
              ├─ imagen_url (Supabase)
              ├─ image_base64 (preview)
              └─ metadata (color, origen, etc.)
```

---

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

**PowerShell:**
```powershell
# Activar entorno virtual (si usas uno)
.\.venv\Scripts\Activate.ps1

# Instalar PyTorch (CPU o GPU según tu hardware)
# CPU:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# GPU (CUDA 11.8 - verificar versión en nvidia-smi):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Instalar dependencias adicionales
pip install opencv-python pillow numpy requests djangorestframework

# Instalar Segment Anything desde GitHub
pip install git+https://github.com/facebookresearch/segment-anything.git
```

### 2. Descargar Checkpoint SAM

Meta ofrece 3 modelos SAM (diferentes tamaños/velocidad):

| Modelo | Tamaño | Velocidad | Precisión | Descarga |
|--------|--------|-----------|-----------|----------|
| `vit_h` | ~2.4GB | Lento | Máxima | [sam_vit_h_4b8939.pth](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth) |
| `vit_l` | ~1.2GB | Medio | Alta | [sam_vit_l_0b3195.pth](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth) |
| `vit_b` | ~375MB | Rápido | Buena | [sam_vit_b_01ec64.pth](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth) |

**Recomendación:**
- **Desarrollo/pruebas**: `vit_b` (más rápido, menor consumo RAM)
- **Producción**: `vit_h` (máxima calidad)

**Descargar con PowerShell:**
```powershell
# Crear directorio para modelos
New-Item -ItemType Directory -Force -Path C:\models

# Descargar vit_h (recomendado)
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth" -OutFile "C:\models\sam_vit_h.pth"

# O vit_b (más ligero)
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth" -OutFile "C:\models\sam_vit_b.pth"
```

### 3. Configurar Variables de Entorno

**Método 1: Variable de sesión (PowerShell)**
```powershell
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
$env:SAM_MODEL_TYPE = 'vit_h'  # o 'vit_l', 'vit_b'
```

**Método 2: Variable permanente (Windows)**
```powershell
# Persistir en perfil de usuario
[System.Environment]::SetEnvironmentVariable('SAM_CHECKPOINT', 'C:\models\sam_vit_h.pth', 'User')
[System.Environment]::SetEnvironmentVariable('SAM_MODEL_TYPE', 'vit_h', 'User')
```

**Método 3: Archivo `.env` (recomendado para desarrollo)**
```env
# .env en la raíz del proyecto
SAM_CHECKPOINT=C:\models\sam_vit_h.pth
SAM_MODEL_TYPE=vit_h
```

### 4. Configurar Supabase (opcional pero recomendado)

Editar `core/utils/supabase_storage.py`:

```python
# Cambiar a True para habilitar Supabase
USE_SUPABASE = True
```

Asegurarte de tener en `.env`:
```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-anon-publica
```

---

## 📖 Uso de la API

### Endpoint

```
POST /dashboard/api/variante/<variante_id>/generar-color/
```

### Parámetros

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `image` | File | No* | Imagen a procesar (PNG/JPG/JPEG) |
| `color` | String | No | Color objetivo en hex (ej: `#ff0000`, `#00ff00`) |

*Si no se envía `image`, usa la imagen de la variante/producto existente

### Ejemplos de Uso

#### 1. **Procesar imagen existente con nuevo color**

**cURL (PowerShell):**
```powershell
$varianteId = 123
$color = "#ff0000"  # Rojo

curl -X POST "http://127.0.0.1:8000/dashboard/api/variante/$varianteId/generar-color/" `
  -H "Cookie: sessionid=tu-session-id" `
  -F "color=$color"
```

**JavaScript (Fetch API):**
```javascript
const varianteId = 123;
const color = '#ff0000';

const formData = new FormData();
formData.append('color', color);

fetch(`/dashboard/api/variante/${varianteId}/generar-color/`, {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: formData
})
.then(res => res.json())
.then(data => {
  console.log('Imagen procesada:', data.imagen_url);
  // Mostrar preview: data.image_base64
});
```

#### 2. **Subir imagen personalizada**

**cURL:**
```powershell
curl -X POST "http://127.0.0.1:8000/dashboard/api/variante/123/generar-color/" `
  -H "Cookie: sessionid=..." `
  -F "image=@C:\ruta\a\zapato.jpg" `
  -F "color=#0000ff"
```

**JavaScript con input file:**
```javascript
const fileInput = document.getElementById('imageUpload');
const colorInput = document.getElementById('colorPicker');

const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('color', colorInput.value);

fetch(`/dashboard/api/variante/123/generar-color/`, {
  method: 'POST',
  headers: { 'X-CSRFToken': getCookie('csrftoken') },
  body: formData
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    document.getElementById('preview').src = data.image_base64;
    console.log('Nueva imagen en:', data.imagen_url);
  }
});
```

### Respuesta Exitosa

```json
{
  "success": true,
  "mensaje": "Imagen recolorizada a #ff0000 usando SAM (origen: producto_url)",
  "imagen_url": "https://tu-proyecto.supabase.co/storage/v1/object/public/media/variantes/recolor_45_123_ff0000.png",
  "imagen_generada_ia": true,
  "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSU...",
  "variante_id": 123,
  "color_aplicado": "#ff0000"
}
```

### Respuesta de Error

```json
{
  "success": false,
  "mensaje": "SAM no disponible: Checkpoint SAM no encontrado. Defina la variable de entorno `SAM_CHECKPOINT` con la ruta al .pth"
}
```

---

## 🎨 Integración Frontend

### Ejemplo Completo: Selector de Color para Variantes

```html
<!-- templates/dashboard/gestionar_variantes.html -->
<div class="variante-item" data-variante-id="{{ variante.id }}">
  <img id="img-{{ variante.id }}" src="{{ variante.imagen_url }}" alt="Variante">
  <h3>{{ variante.color }} - {{ variante.talla }}</h3>
  
  <!-- Selector de color -->
  <input type="color" id="color-{{ variante.id }}" value="{{ variante.color|default:'#ff0000' }}">
  <button onclick="recolorVariante({{ variante.id }})">🎨 Cambiar Color con IA</button>
  
  <!-- Loader -->
  <div id="loader-{{ variante.id }}" class="loader" style="display:none;">
    Procesando con IA...
  </div>
</div>

<script>
function recolorVariante(varianteId) {
  const colorInput = document.getElementById(`color-${varianteId}`);
  const imgElement = document.getElementById(`img-${varianteId}`);
  const loader = document.getElementById(`loader-${varianteId}`);
  
  const formData = new FormData();
  formData.append('color', colorInput.value);
  
  // Mostrar loader
  loader.style.display = 'block';
  imgElement.style.opacity = '0.5';
  
  fetch(`/dashboard/api/variante/${varianteId}/generar-color/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      // Actualizar imagen con preview base64
      imgElement.src = data.image_base64;
      imgElement.style.opacity = '1';
      loader.style.display = 'none';
      
      // Notificación
      alert(`✅ Color cambiado a ${data.color_aplicado}!\nImagen guardada en Supabase`);
    } else {
      alert(`❌ Error: ${data.mensaje}`);
      loader.style.display = 'none';
      imgElement.style.opacity = '1';
    }
  })
  .catch(err => {
    console.error('Error:', err);
    alert('Error de conexión');
    loader.style.display = 'none';
    imgElement.style.opacity = '1';
  });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
</script>

<style>
.loader {
  text-align: center;
  font-weight: bold;
  color: #007bff;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
```

---

## ⚙️ Optimización y Producción

### 1. **Usar GPU para Acelerar SAM**

SAM funciona mejor con GPU NVIDIA. Verifica que tengas CUDA instalado:

```powershell
nvidia-smi  # Ver GPU y versión CUDA
```

Instalar PyTorch con soporte CUDA:
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Para usar GPU en `sam_recolor.py`, el modelo se carga automáticamente en GPU si está disponible.

### 2. **Procesamiento Asíncrono con Celery**

Para grandes volúmenes o evitar timeouts, usa Celery:

**`dashboard/tasks.py`:**
```python
from celery import shared_task
from django.core.files.base import ContentFile
from .sam_recolor import process_image_recolor
from carrito.models import ProductoVariante
from core.utils.supabase_storage import subir_a_supabase
import io

@shared_task
def recolorizar_variante_async(variante_id, color_hex, imagen_bytes=None):
    """Tarea asíncrona para recolorizar variante"""
    from PIL import Image
    
    variante = ProductoVariante.objects.get(id=variante_id)
    
    # Cargar imagen
    if imagen_bytes:
        pil = Image.open(io.BytesIO(imagen_bytes))
    else:
        # Usar imagen existente
        if variante.imagen_url:
            import requests
            resp = requests.get(variante.imagen_url)
            pil = Image.open(io.BytesIO(resp.content))
        else:
            raise ValueError('No hay imagen disponible')
    
    # Procesar
    resultado = process_image_recolor(pil, color_hex)
    
    # Subir a Supabase
    buf = io.BytesIO()
    resultado.save(buf, format='PNG')
    buf.seek(0)
    
    filename = f'variantes/recolor_{variante.producto.id}_{variante.id}_{color_hex.replace("#", "")}.png'
    file_content = ContentFile(buf.getvalue(), name=filename)
    nueva_url = subir_a_supabase(file_content)
    
    # Actualizar variante
    variante.imagen_url = nueva_url
    variante.imagen_generada_ia = True
    variante.save()
    
    return {'success': True, 'imagen_url': nueva_url}
```

**Vista modificada:**
```python
from .tasks import recolorizar_variante_async

def generar_imagen_color(request, variante_id):
    # ... código de carga de imagen ...
    
    # Lanzar tarea asíncrona
    task = recolorizar_variante_async.delay(
        variante_id, 
        target_color,
        pil_image.tobytes() if pil_image else None
    )
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Procesamiento iniciado',
        'task_id': task.id,
        'status_url': f'/dashboard/api/task-status/{task.id}/'
    })
```

### 3. **Caché de Modelos**

SAM se carga una vez en memoria al inicio (implementado en `sam_recolor.py`). Para múltiples workers, considera:
- Redis/Memcached para coordinar caché
- Modelo cargado en GPU compartida

### 4. **Limitaciones y Throttling**

Añadir límites de rate para evitar abuso:

```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

@login_required
def generar_imagen_color(request, variante_id):
    # Rate limiting simple con caché
    cache_key = f'recolor_limit_{request.user.id}'
    count = cache.get(cache_key, 0)
    
    if count >= 10:  # Máximo 10 por hora
        return JsonResponse({
            'success': False,
            'mensaje': 'Límite de procesamiento alcanzado. Espera 1 hora.'
        }, status=429)
    
    cache.set(cache_key, count + 1, 3600)  # 1 hora
    
    # ... resto del código ...
```

---

## 🐛 Troubleshooting

### Error: "segment-anything no está instalado"

```powershell
pip install git+https://github.com/facebookresearch/segment-anything.git
```

### Error: "Checkpoint SAM no encontrado"

Verifica que la variable de entorno esté definida:
```powershell
echo $env:SAM_CHECKPOINT
# Debe mostrar: C:\models\sam_vit_h.pth
```

Si no aparece:
```powershell
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
```

### Procesamiento muy lento (CPU)

SAM es **extremadamente lento en CPU** (puede tardar 30-60 segundos por imagen). Soluciones:

1. **Usar GPU** (recomendado):
   ```powershell
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Usar modelo más pequeño** (`vit_b`):
   ```powershell
   $env:SAM_MODEL_TYPE = 'vit_b'
   $env:SAM_CHECKPOINT = 'C:\models\sam_vit_b.pth'
   ```

3. **Procesar en background** con Celery (ver sección arriba)

### Error: "CUDA out of memory"

El modelo SAM consume mucha VRAM. Opciones:

1. Usar modelo más pequeño (`vit_b`)
2. Reducir resolución de imagen antes de procesar:
   ```python
   # En sam_recolor.py, antes de generate
   max_size = 1024
   pil_image.thumbnail((max_size, max_size), Image.LANCZOS)
   ```

### Máscaras incorrectas

Si SAM no detecta bien el objeto:

1. **Mejorar la imagen origen**: fondo simple, buena iluminación
2. **Usar prompt manual** (requiere modificar `sam_recolor.py` para usar `SamPredictor` con puntos/cajas en lugar de `AutomaticMaskGenerator`)
3. **Fine-tune SAM** con dataset de moda (avanzado)

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [Segment Anything (SAM) - Meta AI](https://github.com/facebookresearch/segment-anything)
- [SAM Paper](https://arxiv.org/abs/2304.02643)
- [Demo interactivo](https://segment-anything.com/)

### Alternativas y Mejoras Futuras

1. **DeepLab v3+** (segmentación por tipo de prenda):
   ```python
   from torchvision.models.segmentation import deeplabv3_resnet101
   model = deeplabv3_resnet101(pretrained=True)
   ```

2. **Stable Diffusion Inpainting** (mayor realismo):
   - Usar `diffusers` de HuggingFace
   - Más costoso pero resultados foto-realistas

3. **ControlNet** (control preciso):
   - Combina SAM + ControlNet para preservar estructura

### Ejemplos de Código

Ver repositorio de ejemplos:
- [Awesome SAM Examples](https://github.com/facebookresearch/segment-anything/tree/main/notebooks)

---

## 📄 Licencia y Créditos

- **SAM**: Apache 2.0 License (Meta AI Research)
- **Django**: BSD License
- **Proyecto**: [Tu Licencia]

---

## 🆘 Soporte

Para problemas específicos del proyecto, contactar:
- Email: [tu-email]
- Issues: [GitHub Issues]
- Documentación adicional: Ver archivos `GUIA_*.md` en el proyecto
