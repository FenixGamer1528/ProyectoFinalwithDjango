@echo off
REM ========================================
REM Script para actualizar servidor remoto
REM ========================================

echo.
echo ========================================
echo   ACTUALIZACION REMOTA DEL SERVIDOR
echo ========================================
echo.

REM Configuracion (EDITA ESTOS VALORES)
set SERVER_USER=tu_usuario
set SERVER_HOST=app.glamoure.tech
set PROJECT_PATH=/ruta/del/proyecto/ProyectoFinalwithDjango

echo Conectando al servidor %SERVER_HOST%...
echo.

REM Ejecutar comandos remotos
ssh %SERVER_USER%@%SERVER_HOST% "cd %PROJECT_PATH% && git pull origin master && python fix_production_db.py && python manage.py migrate carrito --fake && sudo systemctl restart gunicorn"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ACTUALIZACION COMPLETADA
    echo ========================================
    echo.
    echo El servidor se ha actualizado correctamente.
    echo Prueba hacer un pago en: http://app.glamoure.tech
) else (
    echo.
    echo ========================================
    echo   ERROR EN LA ACTUALIZACION
    echo ========================================
    echo.
    echo Revisa la configuracion y vuelve a intentar.
)

pause
