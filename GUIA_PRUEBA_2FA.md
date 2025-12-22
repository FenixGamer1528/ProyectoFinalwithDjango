# 🧪 Guía de Prueba del Sistema 2FA

## ✅ Pasos para Probar 2FA

### Opción 1: Registro Nuevo con 2FA

1. **Ir al registro**
   - Navega a: http://127.0.0.1:8000/registro/
   
2. **Completar formulario**
   - Usuario: `test2fa`
   - Email: `test2fa@example.com`
   - Contraseña: `password123`
   - Confirmar contraseña: `password123`
   - ✅ Marcar checkbox "Activar Autenticación de Dos Factores (2FA)"

3. **Configurar 2FA**
   - Descargar una app autenticadora:
     - Google Authenticator (recomendado)
     - Microsoft Authenticator
     - Authy
   - Escanear el código QR mostrado
   - O copiar la clave secreta manualmente
   - Ingresar el código de 6 dígitos que aparece en la app

4. **Verificar activación**
   - Deberías ver mensaje "¡2FA Activado!"
   - Automáticamente se inicia sesión

### Opción 2: Activar 2FA desde el Dashboard

1. **Iniciar sesión** con un usuario existente
   - http://127.0.0.1:8000/login/

2. **Ir al Dashboard**
   - Clic en "Mi Dashboard" o
   - http://127.0.0.1:8000/dashboard/cliente/

3. **Acceder a Seguridad**
   - Clic en "Seguridad (2FA)" en el menú lateral

4. **Activar 2FA**
   - Clic en botón "Activar 2FA"
   - Escanear código QR con tu app
   - Ingresar código de verificación
   - Confirmar

### Opción 3: Probar Login con 2FA

1. **Cerrar sesión**
   - Clic en "Cerrar Sesión"

2. **Intentar login**
   - Usuario: `test2fa` (o el que creaste)
   - Contraseña: tu contraseña
   - Clic en "Iniciar Sesión"

3. **Ingresar código 2FA**
   - El sistema detecta que tienes 2FA activado
   - Muestra campo para código de 6 dígitos
   - Abre tu app autenticadora
   - Ingresa el código actual (cambia cada 30 segundos)
   - Clic en "Verificar 2FA"

4. **Acceso concedido**
   - Si el código es correcto, accedes normalmente

## 🔍 Verificaciones Importantes

### ✅ Checklist de Funcionamiento

- [ ] El checkbox de 2FA aparece en el registro
- [ ] Se genera código QR correctamente
- [ ] Se puede copiar la clave secreta
- [ ] La app autenticadora reconoce el código QR
- [ ] El código de verificación funciona
- [ ] Se activa 2FA correctamente
- [ ] El login solicita código 2FA
- [ ] Los códigos incorrectos son rechazados
- [ ] Se puede desactivar 2FA desde el dashboard
- [ ] El indicador de estado aparece en el dashboard

### 📱 Apps Autenticadoras Recomendadas

**Google Authenticator**
- iOS: https://apps.apple.com/app/google-authenticator/id388497605
- Android: https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2

**Microsoft Authenticator**
- iOS: https://apps.apple.com/app/microsoft-authenticator/id983156458
- Android: https://play.google.com/store/apps/details?id=com.azure.authenticator

**Authy**
- iOS: https://apps.apple.com/app/authy/id494168017
- Android: https://play.google.com/store/apps/details?id=com.authy.authy
- Desktop: https://authy.com/download/

## 🐛 Solución de Problemas

### El código QR no se escanea
- **Solución**: Usa la opción de copia manual de la clave secreta
- Copia el código que aparece debajo del QR
- En la app, selecciona "Ingresar clave manualmente"
- Pega el código

### Código incorrecto al verificar
- **Causa**: El código cambió (expiran cada 30 segundos)
- **Solución**: Espera a que aparezca un nuevo código e ingrésalo rápidamente

### No puedo acceder con 2FA
- **Solución temporal**: Como administrador, puedes desactivar 2FA directamente en la base de datos:
  ```python
  from carrito.models import UsuarioPersonalizado
  user = UsuarioPersonalizado.objects.get(username='test2fa')
  user.two_factor_enabled = False
  user.save()
  ```

### El servidor muestra errores
- Verifica que las dependencias estén instaladas:
  ```bash
  pip install django-otp qrcode[pil] pyotp
  ```
- Verifica que las migraciones se aplicaron:
  ```bash
  python manage.py migrate
  ```

## 🎓 Escenarios de Prueba

### Escenario 1: Usuario Nuevo sin 2FA
1. Registrarse SIN marcar el checkbox
2. Verificar que el login funciona normalmente
3. Verificar que puede activar 2FA después desde el dashboard

### Escenario 2: Usuario con 2FA Olvida su App
1. Usuario tiene 2FA activado
2. No tiene acceso a la app autenticadora
3. Administrador debe desactivar 2FA manualmente
4. Usuario puede iniciar sesión y reconfigurar 2FA

### Escenario 3: Activar y Desactivar 2FA
1. Usuario sin 2FA
2. Activar desde dashboard
3. Cerrar sesión y verificar que pide código
4. Volver a dashboard y desactivar 2FA
5. Verificar que el login ya no pide código

## 📊 Indicadores Visuales

Busca estos elementos en la UI:

1. **En Registro**:
   - Checkbox con ícono de escudo
   - Texto descriptivo sobre 2FA

2. **En Setup 2FA**:
   - Código QR visible
   - Clave secreta copiable
   - Campo para código de 6 dígitos

3. **En Login con 2FA**:
   - Mensaje azul indicando que se requiere 2FA
   - Campo especial para código (grande, centrado)
   - Botón cambia a "Verificar 2FA"

4. **En Dashboard**:
   - Opción "Seguridad (2FA)" en menú lateral
   - Badge verde con ✓ si está activado
   - Sin badge si está desactivado

## 🎉 Resultado Esperado

Al completar todas las pruebas, deberías tener:

- ✅ Sistema 2FA funcionando en registro
- ✅ Sistema 2FA funcionando en login
- ✅ Gestión de 2FA desde dashboard
- ✅ Indicadores visuales correctos
- ✅ Experiencia de usuario fluida
- ✅ Seguridad mejorada sin afectar usabilidad

---

**¡Disfruta de tu sistema más seguro!** 🔒
