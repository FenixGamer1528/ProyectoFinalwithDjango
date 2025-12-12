# 🎨 IA DE RECOLORIZACIÓN - GUÍA RÁPIDA

## ✨ ¿Qué hace?

Genera automáticamente imágenes en diferentes colores para tus productos usando Inteligencia Artificial (Segment Anything Model de Meta).

---

## 🚀 Uso Rápido

### Para NUEVOS Productos (Automático)

```python
# Solo crea la variante - la imagen se genera SOLA
ProductoVariante.objects.create(
    producto=mi_producto,
    talla='M',
    color='rojo',  # ← Se convierte a #FF0000 y genera imagen
    stock=10
)
# ✅ Imagen generada automáticamente en background
```

### Para Productos EXISTENTES (Comando)

```powershell
# Opción 1: Menú interactivo
.\generar_imagenes_ia.ps1

# Opción 2: Comando directo
python manage.py generar_imagenes_ia
```

---

## 📋 Menú Interactivo

```
╔════════════════════════════════════════════════════════════╗
║     🎨 GENERADOR DE IMÁGENES CON IA - GLAMOURE            ║
╚════════════════════════════════════════════════════════════╝

Selecciona una opción:

  1) 🔄 Procesar TODAS las variantes sin imagen
  2) 📦 Procesar un producto específico (por ID)
  3) 🎨 Procesar por color
  4) 🧪 Procesar solo 10 variantes (prueba)
  5) 🔥 Regenerar TODAS las imágenes (FORCE)
  6) 📊 Ver estadísticas de caché
  7) ❓ Ver ayuda del comando
  0) 🚪 Salir
```

---

## 🎯 Comandos Útiles

```powershell
# Procesar todo
python manage.py generar_imagenes_ia

# Por producto
python manage.py generar_imagenes_ia --producto-id 45

# Por color
python manage.py generar_imagenes_ia --color rojo

# Solo 10 (prueba)
python manage.py generar_imagenes_ia --limit 10

# Regenerar todo
python manage.py generar_imagenes_ia --force
```

---

## 🔧 Configuración (Solo una vez)

```powershell
# 1. Instalar dependencias
pip install torch torchvision opencv-python pillow numpy
pip install git+https://github.com/facebookresearch/segment-anything.git

# 2. Descargar modelo SAM
.\setup_sam_recolor.ps1

# O manual:
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth" -OutFile "C:\models\sam_vit_h.pth"

# 3. Configurar variables
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
$env:SAM_MODEL_TYPE = 'vit_h'
```

---

## ✅ Verificar Configuración

```powershell
# Ver variables
echo $env:SAM_CHECKPOINT
echo $env:SAM_MODEL_TYPE

# Verificar archivo
Test-Path $env:SAM_CHECKPOINT

# Ver estadísticas
.\generar_imagenes_ia.ps1
# → Opción 6
```

---

## 📚 Documentación Completa

- `GUIA_IA_AUTOMATICA.md` - Guía completa con ejemplos
- `SISTEMA_RECOLORIZACION_IA.md` - Documentación técnica
- `README_RECOLORIZACION.md` - Quick start original

---

## 🐛 Problemas Comunes

### "SAM no disponible"
```powershell
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_h.pth'
$env:SAM_MODEL_TYPE = 'vit_h'
```

### "segment-anything no instalado"
```powershell
pip install git+https://github.com/facebookresearch/segment-anything.git
```

### Muy lento
```powershell
# Cambiar a modelo ligero (vit_b)
$env:SAM_CHECKPOINT = 'C:\models\sam_vit_b.pth'
$env:SAM_MODEL_TYPE = 'vit_b'
```

---

**¡Listo! Ahora tus productos se recolorizan automáticamente con IA! 🎨✨**
