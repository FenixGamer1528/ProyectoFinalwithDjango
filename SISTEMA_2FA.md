# 🔒 Sistema de Autenticación de Dos Factores (2FA) - Glamoure

## 📋 Resumen

Se ha implementado un sistema completo de autenticación de dos factores (2FA) utilizando códigos TOTP (Time-based One-Time Password) para mejorar la seguridad de las cuentas de usuario.

## ✨ Características Implementadas

### 1. **Registro con Opción de 2FA**
- Los nuevos usuarios pueden activar 2FA durante el proceso de registro
- Opción de checkbox elegante y visible en el formulario de registro
- Flujo automático para configurar 2FA si el usuario lo selecciona

### 2. **Configuración de 2FA**
- Generación automática de clave secreta única por usuario
- Código QR para escanear con apps autenticadoras
- Opción de copiar clave secreta manualmente
- Verificación del código antes de activar 2FA
- Compatible con: Google Authenticator, Microsoft Authenticator, Authy

### 3. **Login con 2FA**
- Detección automática si el usuario tiene 2FA activado
- Solicitud de código de 6 dígitos después de usuario/contraseña
- Validación con ventana de tiempo de ±30 segundos
- Mensajes de error claros y específicos

### 4. **Gestión de 2FA desde el Perfil**
- Vista dedicada para activar/desactivar 2FA
- Regeneración de códigos QR
- Opción de desactivar 2FA con confirmación
- Indicador visual del estado de 2FA en el dashboard

## 📁 Archivos Modificados/Creados

### Modelos
- `carrito/models.py`: Agregados campos `two_factor_enabled` y `two_factor_secret` a `UsuarioPersonalizado`

### Formularios
- `core/forms.py`:
  - Actualizado `LoginForm` con campo `otp_code`
  - Actualizado `RegistroForm` con campo `enable_2fa`
  - Nuevo `TwoFactorVerifyForm` para verificación de códigos

### Vistas
- `core/views.py`:
  - `login_view`: Actualizada para soportar 2FA
  - `registro_view`: Actualizada para redirigir a setup 2FA
  - `setup_2fa`: Nueva vista para configurar 2FA en el registro
  - `manage_2fa`: Nueva vista para gestionar 2FA desde el perfil

### Templates
- `core/templates/core/login.html`: Actualizado con campo de 2FA condicional
- `core/templates/core/registro.html`: Agregado checkbox para activar 2FA
- `core/templates/core/setup_2fa.html`: Nueva plantilla para configuración inicial
- `core/templates/core/2fa_success.html`: Nueva plantilla de confirmación
- `core/templates/core/manage_2fa.html`: Nueva plantilla para gestión de 2FA
- `dashboard/templates/dashboard/cliente_dashboard.html`: Agregado enlace a gestión de 2FA

### URLs
- `core/urls.py`: Agregadas rutas `setup_2fa` y `manage_2fa`

### Base de Datos
- Nueva migración: `0007_usuariopersonalizado_two_factor_enabled_and_more.py`

## 🚀 Flujos de Usuario

### Flujo 1: Registro con 2FA
1. Usuario completa formulario de registro
2. Marca checkbox "Activar 2FA"
3. Envía formulario
4. Se redirige a página de configuración 2FA
5. Escanea código QR o ingresa clave manualmente
6. Ingresa código de verificación de 6 dígitos
7. Sistema valida y activa 2FA
8. Usuario es redirigido al inicio con sesión iniciada

### Flujo 2: Login con 2FA Activado
1. Usuario ingresa usuario y contraseña
2. Sistema detecta que tiene 2FA activado
3. Muestra campo para código 2FA
4. Usuario ingresa código de 6 dígitos
5. Sistema valida el código TOTP
6. Usuario accede a su cuenta

### Flujo 3: Activar 2FA desde Perfil
1. Usuario accede a Dashboard
2. Hace clic en "Seguridad (2FA)"
3. Hace clic en "Activar 2FA"
4. Escanea código QR
5. Ingresa código de verificación
6. 2FA queda activado

### Flujo 4: Desactivar 2FA
1. Usuario accede a "Seguridad (2FA)"
2. Hace clic en "Desactivar 2FA"
3. Confirma la acción
4. 2FA queda desactivado

## 🔧 Dependencias Instaladas

```bash
pip install django-otp qrcode[pil] pyotp
```

- **django-otp**: Framework para autenticación de dos factores en Django
- **qrcode[pil]**: Generación de códigos QR con soporte de imágenes
- **pyotp**: Generación y verificación de códigos TOTP

## 💡 Características Técnicas

### Seguridad
- Códigos TOTP basados en tiempo (30 segundos)
- Ventana de validación de ±1 intervalo (total 90 segundos)
- Secretos únicos por usuario (32 caracteres base32)
- Almacenamiento seguro de secretos en base de datos
- Sin exposición de claves en URLs o logs

### UX/UI
- Diseño consistente con el tema dorado/negro de Glamoure
- Códigos QR claros y escaneables
- Opción de copia manual de clave secreta
- Mensajes de error específicos y útiles
- Indicadores visuales del estado de 2FA
- Formularios responsivos y accesibles

### Compatibilidad
- Google Authenticator (iOS/Android)
- Microsoft Authenticator (iOS/Android)
- Authy (iOS/Android/Desktop)
- Cualquier app compatible con TOTP RFC 6238

## 📝 Notas de Uso

### Para Usuarios
- Se recomienda activar 2FA para mayor seguridad
- Guardar códigos de respaldo (funcionalidad futura)
- Usar apps autenticadoras confiables
- No compartir códigos QR ni claves secretas

### Para Administradores
- Los campos de 2FA se agregan automáticamente a usuarios existentes
- Usuarios sin 2FA pueden seguir usando login normal
- No hay cambios breaking en el sistema actual
- 2FA es completamente opcional

## 🎯 Ventajas del Sistema

1. **Mayor Seguridad**: Protección adicional contra accesos no autorizados
2. **Facilidad de Uso**: Configuración en menos de 2 minutos
3. **Estándar de Industria**: Uso de TOTP compatible con apps populares
4. **Opcional**: No interrumpe el flujo de usuarios que no lo desean
5. **Visual**: Indicadores claros del estado de seguridad
6. **Profesional**: Implementación completa y robusta

## 🔮 Futuras Mejoras Posibles

- [ ] Códigos de recuperación/backup
- [ ] Verificación por SMS como alternativa
- [ ] Autenticación biométrica
- [ ] Historial de inicios de sesión
- [ ] Notificaciones de actividad sospechosa
- [ ] Múltiples dispositivos 2FA
- [ ] Exportar códigos de respaldo

## 📊 Estado de Implementación

✅ Modelo de base de datos actualizado
✅ Formularios creados y validados
✅ Vistas implementadas
✅ Templates diseñados
✅ URLs configuradas
✅ Migraciones aplicadas
✅ Integración con login/registro
✅ Dashboard actualizado
✅ Documentación completada

---

**Fecha de Implementación**: 11 de Diciembre, 2025
**Versión**: 1.0
**Desarrollado para**: Glamoure Store
