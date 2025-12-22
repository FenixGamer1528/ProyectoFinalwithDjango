#!/bin/bash
# ========================================
# Script para actualizar servidor remoto
# ========================================

# Configuración (EDITA ESTOS VALORES)
SERVER_USER="tu_usuario"
SERVER_HOST="app.glamoure.tech"
PROJECT_PATH="/ruta/del/proyecto/ProyectoFinalwithDjango"

echo ""
echo "========================================"
echo "  ACTUALIZACIÓN REMOTA DEL SERVIDOR"
echo "========================================"
echo ""

echo "Conectando al servidor $SERVER_HOST..."
echo ""

# Ejecutar comandos remotos
ssh $SERVER_USER@$SERVER_HOST << 'EOF'
cd $PROJECT_PATH
echo "📥 Haciendo pull..."
git pull origin master

echo ""
echo "🔧 Ejecutando script de reparación..."
python fix_production_db.py

echo ""
echo "📦 Aplicando migraciones..."
python manage.py migrate carrito --fake

echo ""
echo "🔄 Reiniciando servidor..."
sudo systemctl restart gunicorn

echo ""
echo "✅ Actualización completada"
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "  ACTUALIZACIÓN COMPLETADA"
    echo "========================================"
    echo ""
    echo "El servidor se ha actualizado correctamente."
    echo "Prueba hacer un pago en: http://app.glamoure.tech"
else
    echo ""
    echo "========================================"
    echo "  ERROR EN LA ACTUALIZACIÓN"
    echo "========================================"
    echo ""
    echo "Revisa la configuración y vuelve a intentar."
fi
