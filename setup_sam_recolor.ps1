# Script de Instalación del Sistema de Recolorización IA
# Ejecutar en PowerShell: .\setup_sam_recolor.ps1

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Setup Sistema Recolorización IA   " -ForegroundColor Cyan
Write-Host "  Segment Anything + Django          " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python no encontrado. Instalar desde https://python.org" -ForegroundColor Red
    exit 1
}

# 2. Activar entorno virtual si existe
Write-Host ""
Write-Host "[2/6] Activando entorno virtual..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
    Write-Host "✓ Entorno virtual activado" -ForegroundColor Green
} else {
    Write-Host "⚠ No hay entorno virtual. ¿Crear uno? (s/n)" -ForegroundColor Yellow
    $crear = Read-Host
    if ($crear -eq "s") {
        python -m venv .venv
        & .\.venv\Scripts\Activate.ps1
        Write-Host "✓ Entorno virtual creado y activado" -ForegroundColor Green
    } else {
        Write-Host "⚠ Continuando sin entorno virtual" -ForegroundColor Yellow
    }
}

# 3. Verificar GPU/CUDA
Write-Host ""
Write-Host "[3/6] Verificando GPU NVIDIA..." -ForegroundColor Yellow
$nvidiaSmi = nvidia-smi 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ GPU NVIDIA detectada" -ForegroundColor Green
    Write-Host "⚠ Instalando PyTorch con CUDA 11.8..." -ForegroundColor Yellow
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
} else {
    Write-Host "⚠ No se detectó GPU NVIDIA. Instalando PyTorch CPU..." -ForegroundColor Yellow
    Write-Host "  ADVERTENCIA: SAM será MUY LENTO en CPU (30-60s por imagen)" -ForegroundColor Red
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
}

# 4. Instalar dependencias
Write-Host ""
Write-Host "[4/6] Instalando dependencias..." -ForegroundColor Yellow
pip install opencv-python pillow numpy requests djangorestframework

Write-Host ""
Write-Host "Instalando Segment Anything desde GitHub..." -ForegroundColor Yellow
pip install git+https://github.com/facebookresearch/segment-anything.git

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host "✗ Error instalando dependencias" -ForegroundColor Red
    exit 1
}

# 5. Descargar modelo SAM
Write-Host ""
Write-Host "[5/6] Configurando modelo SAM..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Selecciona el modelo SAM a descargar:" -ForegroundColor Cyan
Write-Host "  1) vit_h (~2.4GB) - Máxima calidad [RECOMENDADO PRODUCCIÓN]" -ForegroundColor White
Write-Host "  2) vit_l (~1.2GB) - Buena calidad" -ForegroundColor White
Write-Host "  3) vit_b (~375MB) - Rápido [RECOMENDADO DESARROLLO]" -ForegroundColor White
Write-Host "  4) Ya tengo el modelo descargado" -ForegroundColor Gray
$modelChoice = Read-Host "Opción"

$modelDir = "C:\models"
$modelPath = ""
$modelType = ""

switch ($modelChoice) {
    "1" {
        $modelPath = "$modelDir\sam_vit_h.pth"
        $modelType = "vit_h"
        $url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    }
    "2" {
        $modelPath = "$modelDir\sam_vit_l.pth"
        $modelType = "vit_l"
        $url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth"
    }
    "3" {
        $modelPath = "$modelDir\sam_vit_b.pth"
        $modelType = "vit_b"
        $url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    }
    "4" {
        $modelPath = Read-Host "Ruta completa al archivo .pth"
        $modelType = Read-Host "Tipo de modelo (vit_h, vit_l, vit_b)"
    }
    default {
        Write-Host "✗ Opción inválida" -ForegroundColor Red
        exit 1
    }
}

if ($modelChoice -ne "4") {
    Write-Host ""
    Write-Host "Descargando modelo desde $url..." -ForegroundColor Yellow
    Write-Host "⏳ Esto puede tardar varios minutos..." -ForegroundColor Gray
    
    if (-not (Test-Path $modelDir)) {
        New-Item -ItemType Directory -Force -Path $modelDir | Out-Null
    }
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $modelPath -UseBasicParsing
        Write-Host "✓ Modelo descargado en $modelPath" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error descargando modelo: $_" -ForegroundColor Red
        Write-Host "  Descárgalo manualmente desde: $url" -ForegroundColor Yellow
        exit 1
    }
}

# Verificar que el archivo exista
if (-not (Test-Path $modelPath)) {
    Write-Host "✗ No se encontró el modelo en $modelPath" -ForegroundColor Red
    exit 1
}

# 6. Configurar variables de entorno
Write-Host ""
Write-Host "[6/6] Configurando variables de entorno..." -ForegroundColor Yellow

# Variable de sesión
$env:SAM_CHECKPOINT = $modelPath
$env:SAM_MODEL_TYPE = $modelType

Write-Host "✓ Variables de sesión configuradas" -ForegroundColor Green
Write-Host "  SAM_CHECKPOINT = $modelPath" -ForegroundColor Gray
Write-Host "  SAM_MODEL_TYPE = $modelType" -ForegroundColor Gray

# Preguntar si quiere persistir
Write-Host ""
Write-Host "¿Guardar variables permanentemente en el sistema? (s/n)" -ForegroundColor Yellow
$persist = Read-Host
if ($persist -eq "s") {
    try {
        [System.Environment]::SetEnvironmentVariable('SAM_CHECKPOINT', $modelPath, 'User')
        [System.Environment]::SetEnvironmentVariable('SAM_MODEL_TYPE', $modelType, 'User')
        Write-Host "✓ Variables guardadas permanentemente" -ForegroundColor Green
        Write-Host "  (Reiniciar terminal para que tomen efecto)" -ForegroundColor Gray
    } catch {
        Write-Host "⚠ No se pudieron guardar permanentemente. Usar .env o configurar manualmente" -ForegroundColor Yellow
    }
}

# Crear/actualizar .env
$envFile = ".env"
Write-Host ""
Write-Host "¿Agregar variables a archivo .env? (s/n)" -ForegroundColor Yellow
$addToEnv = Read-Host
if ($addToEnv -eq "s") {
    $envContent = Get-Content $envFile -Raw -ErrorAction SilentlyContinue
    
    if ($envContent -match "SAM_CHECKPOINT") {
        # Actualizar existente
        $envContent = $envContent -replace "SAM_CHECKPOINT=.*", "SAM_CHECKPOINT=$modelPath"
        $envContent = $envContent -replace "SAM_MODEL_TYPE=.*", "SAM_MODEL_TYPE=$modelType"
    } else {
        # Agregar nuevo
        $envContent += "`n`n# Configuración SAM (Recolorización IA)`nSAM_CHECKPOINT=$modelPath`nSAM_MODEL_TYPE=$modelType`n"
    }
    
    Set-Content -Path $envFile -Value $envContent
    Write-Host "✓ Variables agregadas a .env" -ForegroundColor Green
}

# Resumen final
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ✓ INSTALACIÓN COMPLETADA           " -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resumen de configuración:" -ForegroundColor White
Write-Host "  • PyTorch: Instalado $(if ($nvidiaSmi) { '(GPU CUDA)' } else { '(CPU)' })" -ForegroundColor Gray
Write-Host "  • OpenCV: Instalado" -ForegroundColor Gray
Write-Host "  • Segment Anything: Instalado" -ForegroundColor Gray
Write-Host "  • Modelo SAM: $modelType ($modelPath)" -ForegroundColor Gray
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Iniciar servidor Django: python manage.py runserver" -ForegroundColor White
Write-Host "  2. Probar endpoint: POST /dashboard/api/variante/<id>/generar-color/" -ForegroundColor White
Write-Host "  3. Ver documentación completa: SISTEMA_RECOLORIZACION_IA.md" -ForegroundColor White
Write-Host ""

# Verificación rápida
Write-Host "¿Ejecutar verificación rápida? (s/n)" -ForegroundColor Yellow
$verify = Read-Host
if ($verify -eq "s") {
    Write-Host ""
    Write-Host "Verificando instalación..." -ForegroundColor Yellow
    
    python -c "import torch; print('✓ PyTorch:', torch.__version__)"
    python -c "import cv2; print('✓ OpenCV:', cv2.__version__)"
    python -c "import segment_anything; print('✓ Segment Anything instalado')"
    python -c "import os; print('✓ SAM_CHECKPOINT:', os.environ.get('SAM_CHECKPOINT', 'NO CONFIGURADO'))"
    
    Write-Host ""
    Write-Host "✓ Verificación completada" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎨 ¡Listo para usar Recolorización con IA!" -ForegroundColor Cyan
