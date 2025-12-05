# 🎨 Sistema de Recolorización IA - Quick Start

Sistema integrado para cambiar automáticamente el color de productos usando **Segment Anything Model (SAM)** + recolorización HSV.

## ⚡ Instalación Rápida (5 minutos)

### Opción 1: Script Automático (Recomendado)

```powershell
# Ejecutar en PowerShell
.\setup_sam_recolor.ps1
```

El script automáticamente:
- ✅ Verifica Python y GPU
- ✅ Instala PyTorch (CPU o CUDA)
- ✅ Instala Segment Anything
- ✅ Descarga modelo SAM
- ✅ Configura variables de entorno

### Opción 2: Instalación Manual

```powershell
# 1. Instalar dependencias
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install opencv-python pillow numpy requests
pip install git+https://github.com/facebookresearch/segment-anything.git

# 2. Descargar modelo SAM (elegir uno)
# vit_h (2.4GB, máxima calidad):
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth" -OutFile "C:\models\sam_vit_h.pth"

# vit_b (375MB, más rápido):
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth" -OutFile "C:\models\sam_vit_b.pth"

# 3. Configurar variables de entorno
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
$env:SAM_MODEL_TYPE = 'vit_h'
```

## 🧪 Prueba Rápida

### Test Standalone (sin Django)

```powershell
# Probar con una imagen local
python test_sam_standalone.py zapato.jpg "#ff0000"
```

Esto procesará `zapato.jpg` y generará `test_recolor_ff0000.png` con el color rojo aplicado.

### Test con Django

```powershell
# 1. Iniciar servidor
python manage.py runserver

# 2. En otra terminal, probar endpoint
curl -X POST "http://127.0.0.1:8000/dashboard/api/variante/123/generar-color/" `
  -H "Cookie: sessionid=tu-session" `
  -F "color=#0000ff"
```

## 📖 Uso Básico

### Endpoint API

```
POST /dashboard/api/variante/<variante_id>/generar-color/
```

**Parámetros:**
- `image` (opcional): archivo imagen a procesar
- `color` (opcional): color hex (ej: `#ff0000`)

**Respuesta:**
```json
{
  "success": true,
  "mensaje": "Imagen recolorizada a #ff0000",
  "imagen_url": "https://supabase.../recolor_123_ff0000.png",
  "image_base64": "data:image/png;base64,...",
  "variante_id": 123,
  "color_aplicado": "#ff0000"
}
```

### Ejemplo JavaScript

```javascript
const formData = new FormData();
formData.append('color', '#ff0000');

fetch('/dashboard/api/variante/123/generar-color/', {
  method: 'POST',
  headers: { 'X-CSRFToken': getCookie('csrftoken') },
  body: formData
})
.then(res => res.json())
.then(data => {
  console.log('Nueva imagen:', data.imagen_url);
  document.getElementById('preview').src = data.image_base64;
});
```

## 🏗️ Archivos Agregados

```
ProyectoFinalwithDjango/
├── dashboard/
│   └── sam_recolor.py              # Módulo procesamiento SAM
├── SISTEMA_RECOLORIZACION_IA.md    # Documentación completa
├── setup_sam_recolor.ps1           # Script instalación automática
├── test_sam_standalone.py          # Script prueba independiente
└── requirements.txt                # Dependencias actualizadas
```

## ⚙️ Configuración

### Variables de Entorno

```env
SAM_CHECKPOINT=C:\models\sam_vit_h.pth
SAM_MODEL_TYPE=vit_h
```

### Supabase (opcional)

Editar `core/utils/supabase_storage.py`:
```python
USE_SUPABASE = True  # Cambiar a True
```

Agregar a `.env`:
```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-anon
```

## 🚀 Optimización

### GPU (Recomendado)

```powershell
# Verificar GPU
nvidia-smi

# Instalar PyTorch con CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Performance:**
- CPU: ~30-60 segundos por imagen
- GPU: ~2-5 segundos por imagen

### Modelo Más Ligero

Para desarrollo/pruebas, usar `vit_b` (10x más rápido):
```powershell
$env:SAM_MODEL_TYPE = 'vit_b'
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_b.pth'
```

## 🐛 Problemas Comunes

### "segment-anything no está instalado"
```powershell
pip install git+https://github.com/facebookresearch/segment-anything.git
```

### "Checkpoint SAM no encontrado"
```powershell
# Verificar variable
echo $env:SAM_CHECKPOINT

# Redefinir si no aparece
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
```

### Procesamiento muy lento
- **Solución 1**: Usar GPU (ver sección Optimización)
- **Solución 2**: Cambiar a modelo `vit_b`
- **Solución 3**: Implementar Celery para procesamiento asíncrono

### "CUDA out of memory"
- Usar modelo más pequeño (`vit_b`)
- Reducir resolución de imagen
- Cerrar otras aplicaciones GPU

## 📚 Documentación Completa

Ver `SISTEMA_RECOLORIZACION_IA.md` para:
- Arquitectura detallada
- Integración frontend completa
- Procesamiento asíncrono con Celery
- Rate limiting y seguridad
- Alternativas (DeepLab, Stable Diffusion)

## 🔗 Enlaces Útiles

- [Segment Anything GitHub](https://github.com/facebookresearch/segment-anything)
- [Demo SAM Interactivo](https://segment-anything.com/)
- [PyTorch CUDA Installation](https://pytorch.org/get-started/locally/)

## ✅ Checklist de Inicio

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip install ...`)
- [ ] Modelo SAM descargado
- [ ] Variable `SAM_CHECKPOINT` configurada
- [ ] Test standalone exitoso
- [ ] Servidor Django corriendo
- [ ] Endpoint API funcionando

## 🆘 Soporte

Para más ayuda:
1. Revisar `SISTEMA_RECOLORIZACION_IA.md` (guía completa)
2. Ejecutar `python test_sam_standalone.py` para diagnóstico
3. Verificar logs del servidor Django
4. Consultar Issues de [Segment Anything](https://github.com/facebookresearch/segment-anything/issues)

---

**¡Listo para recolorizar productos con IA! 🎨**
