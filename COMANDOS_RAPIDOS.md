# 🚀 COMANDOS RÁPIDOS - Sistema Recolorización IA

## 📦 Instalación Express (Copy-Paste)

### Opción 1: Instalación Automática
```powershell
.\setup_sam_recolor.ps1
```

### Opción 2: Instalación Manual Completa
```powershell
# 1. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 2. Instalar PyTorch (CPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# O para GPU (CUDA 11.8)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 3. Instalar dependencias adicionales
pip install opencv-python pillow numpy requests djangorestframework

# 4. Instalar Segment Anything
pip install git+https://github.com/facebookresearch/segment-anything.git

# 5. Crear directorio para modelos
New-Item -ItemType Directory -Force -Path C:\models

# 6. Descargar modelo SAM (elegir uno)
# vit_h (2.4GB, máxima calidad):
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth" -OutFile "C:\models\sam_vit_h.pth"

# vit_b (375MB, más rápido):
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth" -OutFile "C:\models\sam_vit_b.pth"

# 7. Configurar variables de entorno
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
$env:SAM_MODEL_TYPE = 'vit_h'

# 8. Persistir variables (opcional)
[System.Environment]::SetEnvironmentVariable('SAM_CHECKPOINT', 'C:\models\sam_vit_h.pth', 'User')
[System.Environment]::SetEnvironmentVariable('SAM_MODEL_TYPE', 'vit_h', 'User')
```

---

## 🧪 Pruebas Rápidas

### Test Standalone (sin Django)
```powershell
# Con imagen local
python test_sam_standalone.py zapato.jpg "#ff0000"

# Verificar resultado
start test_recolor_ff0000.png
```

### Test con Django
```powershell
# Terminal 1: Iniciar servidor
python manage.py runserver

# Terminal 2: Probar endpoint con cURL
$varianteId = 123
curl -X POST "http://127.0.0.1:8000/dashboard/api/variante/$varianteId/generar-color/" `
  -H "Cookie: sessionid=TU_SESSION_ID" `
  -F "color=#ff0000"

# O con archivo
curl -X POST "http://127.0.0.1:8000/dashboard/api/variante/$varianteId/generar-color/" `
  -H "Cookie: sessionid=TU_SESSION_ID" `
  -F "image=@C:\ruta\imagen.jpg" `
  -F "color=#0000ff"
```

### Verificar Instalación
```powershell
# Verificar Python
python --version

# Verificar PyTorch
python -c "import torch; print('PyTorch:', torch.__version__)"

# Verificar CUDA (GPU)
python -c "import torch; print('CUDA disponible:', torch.cuda.is_available())"

# Verificar OpenCV
python -c "import cv2; print('OpenCV:', cv2.__version__)"

# Verificar Segment Anything
python -c "import segment_anything; print('SAM instalado')"

# Verificar checkpoint
echo $env:SAM_CHECKPOINT
Test-Path $env:SAM_CHECKPOINT
```

---

## 🎨 Ejemplos de Uso API

### JavaScript - Uso Básico
```javascript
// Recolorizar variante existente
fetch('/dashboard/api/variante/123/generar-color/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: new FormData(document.querySelector('form'))
})
.then(res => res.json())
.then(data => console.log(data.imagen_url));
```

### JavaScript - Con Selector de Color
```javascript
const colorInput = document.getElementById('colorPicker');
const formData = new FormData();
formData.append('color', colorInput.value);

fetch(`/dashboard/api/variante/123/generar-color/`, {
  method: 'POST',
  headers: { 'X-CSRFToken': getCookie('csrftoken') },
  body: formData
})
.then(res => res.json())
.then(data => {
  document.getElementById('preview').src = data.image_base64;
});
```

### JavaScript - Upload de Imagen
```javascript
const fileInput = document.getElementById('imageUpload');
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('color', '#ff0000');

fetch('/dashboard/api/variante/123/generar-color/', {
  method: 'POST',
  headers: { 'X-CSRFToken': getCookie('csrftoken') },
  body: formData
});
```

### Python - Uso Directo del Módulo
```python
from PIL import Image
from dashboard.sam_recolor import process_image_recolor

# Cargar imagen
imagen = Image.open('zapato.jpg')

# Procesar
resultado = process_image_recolor(imagen, '#ff0000')

# Guardar
resultado.save('zapato_rojo.png')
```

---

## 🔧 Configuración Rápida

### Cambiar Modelo SAM
```powershell
# A modelo más ligero (vit_b)
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_b.pth'
$env:SAM_MODEL_TYPE = 'vit_b'

# A modelo pesado (vit_h)
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
$env:SAM_MODEL_TYPE = 'vit_h'
```

### Activar/Desactivar Supabase
```python
# En core/utils/supabase_storage.py
USE_SUPABASE = True   # Activar
USE_SUPABASE = False  # Desactivar
```

### Variables .env
```env
# Agregar a .env
SAM_CHECKPOINT=C:\models\sam_vit_h.pth
SAM_MODEL_TYPE=vit_h

SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-anon
```

---

## 🐛 Diagnóstico Rápido

### GPU no Detectada
```powershell
# Verificar NVIDIA
nvidia-smi

# Reinstalar PyTorch con CUDA
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Verificar en Python
python -c "import torch; print(torch.cuda.is_available())"
```

### Modelo SAM No Encontrado
```powershell
# Verificar variable
echo $env:SAM_CHECKPOINT

# Verificar archivo
Test-Path $env:SAM_CHECKPOINT

# Redefinir si necesario
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
```

### Error de Imports
```powershell
# Reinstalar dependencias
pip install --force-reinstall opencv-python pillow numpy
pip install --force-reinstall git+https://github.com/facebookresearch/segment-anything.git
```

### Procesamiento Lento
```powershell
# Cambiar a modelo más ligero
$env:SAM_MODEL_TYPE = 'vit_b'
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_b.pth'

# O verificar GPU
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No disponible')"
```

---

## 📊 Monitoreo

### Ver Logs Django
```powershell
# Logs en tiempo real
python manage.py runserver --verbosity 2

# O usar logging
tail -f django.log
```

### Monitorear GPU
```powershell
# Ver uso actual
nvidia-smi

# Monitoreo continuo
nvidia-smi -l 1
```

### Verificar Supabase
```python
# En shell de Django
python manage.py shell

from core.utils.supabase_storage import supabase
print(supabase)
```

---

## 🧹 Limpieza y Reset

### Limpiar Caché Python
```powershell
# Eliminar __pycache__
Get-ChildItem -Path . -Include __pycache__ -Recurse | Remove-Item -Recurse -Force
```

### Resetear Variables de Entorno
```powershell
# Eliminar variables de sesión
Remove-Item Env:\SAM_CHECKPOINT
Remove-Item Env:\SAM_MODEL_TYPE

# Eliminar permanentes
[System.Environment]::SetEnvironmentVariable('SAM_CHECKPOINT', $null, 'User')
[System.Environment]::SetEnvironmentVariable('SAM_MODEL_TYPE', $null, 'User')
```

### Desinstalar Todo
```powershell
pip uninstall torch torchvision opencv-python segment-anything -y
Remove-Item -Recurse -Force C:\models
```

---

## 📚 Documentación

### Archivos Importantes
```powershell
# Quick Start
cat README_RECOLORIZACION.md

# Guía Completa
cat SISTEMA_RECOLORIZACION_IA.md

# Resumen
cat RESUMEN_IMPLEMENTACION_IA.md

# Este archivo
cat COMANDOS_RAPIDOS.md
```

### Enlaces Rápidos
- Segment Anything: https://github.com/facebookresearch/segment-anything
- Demo SAM: https://segment-anything.com/
- PyTorch: https://pytorch.org/get-started/locally/

---

## 🎯 Flujo de Trabajo Completo

### Primera Vez (Setup)
```powershell
# 1. Instalar
.\setup_sam_recolor.ps1

# 2. Probar standalone
python test_sam_standalone.py test_image.jpg "#ff0000"

# 3. Iniciar Django
python manage.py runserver

# 4. Probar API
curl -X POST http://127.0.0.1:8000/dashboard/api/variante/1/generar-color/ -F "color=#ff0000"
```

### Desarrollo Diario
```powershell
# Activar entorno
.\.venv\Scripts\Activate.ps1

# Configurar variables (si no están persistidas)
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
$env:SAM_MODEL_TYPE = 'vit_h'

# Iniciar servidor
python manage.py runserver
```

### Producción
```powershell
# Verificar GPU
nvidia-smi

# Usar modelo de alta calidad
$env:SAM_MODEL_TYPE = 'vit_h'

# Iniciar con Gunicorn (ejemplo)
gunicorn glamoure.wsgi:application --workers 2 --bind 0.0.0.0:8000
```

---

## 💡 Tips y Trucos

### Acelerar Primera Carga
```python
# Precargar modelo al iniciar Django
# En settings.py o apps.py
import os
os.environ.setdefault('SAM_CHECKPOINT', 'C:/models/sam_vit_h.pth')

from dashboard.sam_recolor import _load_sam
_load_sam()  # Carga el modelo una vez
```

### Batch Processing
```python
# Script para procesar múltiples variantes
from carrito.models import ProductoVariante
from dashboard.sam_recolor import process_image_recolor
from PIL import Image

for variante in ProductoVariante.objects.filter(imagen_generada_ia=False):
    img = Image.open(variante.producto.imagen.path)
    resultado = process_image_recolor(img, f'#{variante.color}')
    resultado.save(f'output/{variante.id}.png')
```

### Reducir Uso de VRAM
```python
# En sam_recolor.py, añadir después de procesar:
import torch
torch.cuda.empty_cache()
```

---

**¡Todo listo para recolorizar con IA! 🎨**
