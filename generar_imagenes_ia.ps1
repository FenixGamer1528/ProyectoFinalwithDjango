# ========================================
# 🎨 SCRIPT PARA GENERAR IMÁGENES CON IA
# ========================================
# Facilita la ejecución del comando generar_imagenes_ia

param(
    [Parameter()]
    [string]$Accion = "menu",
    
    [Parameter()]
    [int]$ProductoId,
    
    [Parameter()]
    [string]$Color,
    
    [Parameter()]
    [int]$Limit,
    
    [Parameter()]
    [switch]$Force
)

function Mostrar-Menu {
    Clear-Host
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     🎨 GENERADOR DE IMÁGENES CON IA - GLAMOURE            ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Selecciona una opción:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1) 🔄 Procesar TODAS las variantes sin imagen" -ForegroundColor White
    Write-Host "  2) 📦 Procesar un producto específico (por ID)" -ForegroundColor White
    Write-Host "  3) 🎨 Procesar por color" -ForegroundColor White
    Write-Host "  4) 🧪 Procesar solo 10 variantes (prueba)" -ForegroundColor White
    Write-Host "  5) 🔥 Regenerar TODAS las imágenes (FORCE)" -ForegroundColor Red
    Write-Host "  6) 📊 Ver estadísticas de caché" -ForegroundColor Cyan
    Write-Host "  7) ❓ Ver ayuda del comando" -ForegroundColor Gray
    Write-Host "  0) 🚪 Salir" -ForegroundColor Gray
    Write-Host ""
    $opcion = Read-Host "Opción"
    return $opcion
}

function Procesar-Todas {
    Write-Host ""
    Write-Host "🔄 Procesando TODAS las variantes sin imagen..." -ForegroundColor Yellow
    Write-Host ""
    python manage.py generar_imagenes_ia
}

function Procesar-Producto {
    Write-Host ""
    $id = Read-Host "Ingresa el ID del producto"
    Write-Host ""
    Write-Host "📦 Procesando producto ID: $id" -ForegroundColor Yellow
    Write-Host ""
    python manage.py generar_imagenes_ia --producto-id $id
}

function Procesar-Color {
    Write-Host ""
    Write-Host "Colores disponibles: rojo, azul, negro, blanco, verde, amarillo, rosa, morado, gris, beige, café" -ForegroundColor Cyan
    $color = Read-Host "Ingresa el color a procesar"
    Write-Host ""
    Write-Host "🎨 Procesando variantes de color: $color" -ForegroundColor Yellow
    Write-Host ""
    python manage.py generar_imagenes_ia --color $color
}

function Procesar-Prueba {
    Write-Host ""
    Write-Host "🧪 Procesando solo 10 variantes como prueba..." -ForegroundColor Yellow
    Write-Host ""
    python manage.py generar_imagenes_ia --limit 10
}

function Procesar-Force {
    Write-Host ""
    Write-Host "⚠️  ADVERTENCIA: Esto regenerará TODAS las imágenes" -ForegroundColor Red
    Write-Host "    Esto puede tomar mucho tiempo y recursos." -ForegroundColor Yellow
    Write-Host ""
    $confirmacion = Read-Host "¿Estás seguro? (escribe 'SI' para confirmar)"
    
    if ($confirmacion -eq "SI") {
        Write-Host ""
        Write-Host "🔥 Regenerando TODAS las imágenes..." -ForegroundColor Red
        Write-Host ""
        python manage.py generar_imagenes_ia --force
    } else {
        Write-Host ""
        Write-Host "❌ Cancelado por el usuario" -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

function Ver-Estadisticas {
    Write-Host ""
    Write-Host "📊 Consultando estadísticas..." -ForegroundColor Cyan
    Write-Host ""
    
    python -c @"
from carrito.models import ProductoVariante
from dashboard.models import ImagenColorCache

# Variantes sin imagen
sin_imagen = ProductoVariante.objects.filter(imagen='', imagen_url__isnull=True).count()
con_imagen = ProductoVariante.objects.exclude(imagen='', imagen_url__isnull=True).count()
total_variantes = ProductoVariante.objects.count()
generadas_ia = ProductoVariante.objects.filter(imagen_generada_ia=True).count()
cache_total = ImagenColorCache.objects.count()

print('═' * 60)
print('📊 ESTADÍSTICAS DE IMÁGENES')
print('═' * 60)
print(f'Total de variantes: {total_variantes}')
print(f'  • Con imagen: {con_imagen}')
print(f'  • Sin imagen: {sin_imagen}')
print(f'  • Generadas por IA: {generadas_ia}')
print(f'  • En caché: {cache_total}')
print('═' * 60)

if sin_imagen > 0:
    print(f'\n✨ Puedes generar {sin_imagen} imágenes nuevas con IA')
else:
    print('\n✅ ¡Todas las variantes tienen imagen!')
"@
    
    Write-Host ""
    Write-Host "Presiona Enter para continuar..." -ForegroundColor Gray
    Read-Host
}

function Ver-Ayuda {
    Write-Host ""
    Write-Host "📖 AYUDA - Comando generar_imagenes_ia" -ForegroundColor Cyan
    Write-Host ""
    python manage.py help generar_imagenes_ia
    Write-Host ""
    Write-Host "Presiona Enter para continuar..." -ForegroundColor Gray
    Read-Host
}

# ===== EJECUCIÓN PRINCIPAL =====

if ($Accion -eq "menu") {
    # Modo interactivo
    while ($true) {
        $opcion = Mostrar-Menu
        
        switch ($opcion) {
            "1" { Procesar-Todas }
            "2" { Procesar-Producto }
            "3" { Procesar-Color }
            "4" { Procesar-Prueba }
            "5" { Procesar-Force }
            "6" { Ver-Estadisticas; continue }
            "7" { Ver-Ayuda; continue }
            "0" { 
                Write-Host ""
                Write-Host "👋 ¡Hasta luego!" -ForegroundColor Green
                exit 
            }
            default { 
                Write-Host ""
                Write-Host "❌ Opción inválida" -ForegroundColor Red
                Start-Sleep -Seconds 1
                continue
            }
        }
        
        Write-Host ""
        Write-Host "✅ Proceso completado" -ForegroundColor Green
        Write-Host ""
        Write-Host "Presiona Enter para volver al menú..." -ForegroundColor Gray
        Read-Host
    }
} else {
    # Modo comando directo
    $args = @()
    
    if ($ProductoId) {
        $args += "--producto-id"
        $args += $ProductoId
    }
    
    if ($Color) {
        $args += "--color"
        $args += $Color
    }
    
    if ($Limit) {
        $args += "--limit"
        $args += $Limit
    }
    
    if ($Force) {
        $args += "--force"
    }
    
    python manage.py generar_imagenes_ia @args
}
