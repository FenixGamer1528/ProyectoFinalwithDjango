# 🚀 GUÍA DE DEPLOYMENT - CORRECCIÓN CAMPO NUMERO

## ⚠️ PROBLEMA
Error: `null value in column "numero" of relation "carrito_pedido" violates not-null constraint`

El servidor de producción tiene código antiguo que no genera el campo `numero` al crear pedidos.

---

## 📋 PASOS PARA CORREGIR EN PRODUCCIÓN

### 1️⃣ Conectarse al Servidor
```bash
ssh usuario@app.glamoure.tech
# O acceder por el panel de control de tu hosting
```

### 2️⃣ Ir al Directorio del Proyecto
```bash
cd /ruta/del/proyecto/ProyectoFinalwithDjango
# Ejemplo: cd /var/www/ProyectoFinalwithDjango
```

### 3️⃣ Hacer Pull de los Cambios
```bash
git pull origin master
```

Si hay conflictos, usa:
```bash
git stash
git pull origin master
git stash pop
```

### 4️⃣ Ejecutar el Script de Reparación
```bash
python fix_production_db.py
```

Este script:
- ✅ Verifica si la columna `numero` existe
- ✅ Crea la columna si no existe
- ✅ Genera números únicos para pedidos existentes
- ✅ Aplica restricciones NOT NULL y UNIQUE
- ✅ Crea índices necesarios

### 5️⃣ Marcar Migraciones como Aplicadas
```bash
python manage.py migrate carrito --fake
```

### 6️⃣ Reiniciar el Servidor

**Opción A - Gunicorn con Systemd:**
```bash
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

**Opción B - Supervisor:**
```bash
sudo supervisorctl restart glamoure
sudo supervisorctl status glamoure
```

**Opción C - PM2:**
```bash
pm2 restart glamoure
pm2 status
```

**Opción D - Servidor de Desarrollo:**
```bash
pkill -f "python manage.py runserver"
python manage.py runserver 0.0.0.0:8000
```

### 7️⃣ Verificar que Funciona
```bash
# Ver logs en tiempo real
tail -f /var/log/gunicorn/error.log
# O
journalctl -u gunicorn -f
```

Luego prueba hacer un pago en: http://app.glamoure.tech

---

## 🔍 VERIFICACIÓN MANUAL (OPCIONAL)

Si prefieres verificar la base de datos manualmente:

```bash
# Conectar a PostgreSQL
psql -U tu_usuario -d nombre_base_datos

# Verificar estructura
\d carrito_pedido

# Verificar datos
SELECT id, numero, estado, fecha FROM carrito_pedido LIMIT 5;

# Contar pedidos sin número
SELECT COUNT(*) FROM carrito_pedido WHERE numero IS NULL;

# Salir
\q
```

---

## 📝 CAMBIOS REALIZADOS EN EL CÓDIGO

### pagos/views.py (confirmar_pago_carrito)
```python
# Ahora genera explícitamente el número de pedido
numero_pedido = f"PED-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

Pedido.objects.create(
    usuario=transaccion.usuario,
    producto=producto,
    cantidad=prod_data['cantidad'],
    numero=numero_pedido,  # ✅ NUEVO
    total=total_pedido,     # ✅ NUEVO
    estado='pendiente',     # ✅ CAMBIADO (antes era 'confirmado')
    telefono=transaccion.usuario.telefono
)
```

### carrito/models.py (Pedido.save)
```python
# El método save() también genera automáticamente el número
if not self.numero:
    self.numero = f"PED-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
```

---

## ✅ CHECKLIST DE DEPLOYMENT

- [ ] Pull de cambios (`git pull origin master`)
- [ ] Ejecutar script de reparación (`python fix_production_db.py`)
- [ ] Marcar migraciones (`python manage.py migrate carrito --fake`)
- [ ] Reiniciar servidor (gunicorn/supervisor/pm2)
- [ ] Verificar logs sin errores
- [ ] Probar crear un pedido de prueba
- [ ] Verificar que el pedido aparece en el dashboard

---

## 🆘 SI ALGO SALE MAL

### Error: "permission denied"
```bash
sudo python fix_production_db.py
```

### Error: "Django settings not found"
```bash
export DJANGO_SETTINGS_MODULE=glamoure.settings
python fix_production_db.py
```

### Base de datos bloqueada
```bash
# Matar procesos Django que estén corriendo
pkill -f "python manage.py"
```

### Revertir cambios
```bash
git reset --hard HEAD~1
sudo systemctl restart gunicorn
```

---

## 📞 SOPORTE

Si necesitas ayuda adicional:
1. Revisa los logs: `tail -f /var/log/gunicorn/error.log`
2. Verifica el estado del servidor: `sudo systemctl status gunicorn`
3. Comprueba la base de datos: `psql` (ver comandos arriba)

---

**Última actualización:** 27 de noviembre de 2025
**Versión:** 1.0
