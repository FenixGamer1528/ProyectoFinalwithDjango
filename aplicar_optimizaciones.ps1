# Script para aplicar optimizaciones
# Ejecutar: .\aplicar_optimizaciones.ps1

Write-Host "=== Aplicando Optimizaciones de Rendimiento ===" -ForegroundColor Green

# 1. Crear migraciones
Write-Host "`n1. Creando migraciones..." -ForegroundColor Cyan
python manage.py makemigrations

# 2. Aplicar migraciones
Write-Host "`n2. Aplicando migraciones..." -ForegroundColor Cyan
python manage.py migrate

# 3. Recolectar archivos estáticos (opcional)
Write-Host "`n3. ¿Deseas recolectar archivos estáticos? (S/N)" -ForegroundColor Yellow
$respuesta = Read-Host
if ($respuesta -eq "S" -or $respuesta -eq "s") {
    python manage.py collectstatic --noinput
}

Write-Host "`n=== Optimizaciones Aplicadas ===" -ForegroundColor Green
Write-Host "Revisa el archivo OPTIMIZACIONES.md para más detalles" -ForegroundColor Yellow
