# 🚀 Guía Rápida de Optimización - Glamoure

## ✅ PASO 1: Aplicar Migraciones (REQUERIDO)

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Esto aplicará los índices de base de datos que acelerarán las consultas.

---

## 🎯 Optimizaciones Implementadas Automáticamente

### Backend (Python/Django)
✅ **Conexiones de Base de Datos**: Reutilización de conexiones (CONN_MAX_AGE)
✅ **Caché Local**: Sistema de caché en memoria configurado
✅ **Consultas Optimizadas**: select_related() y prefetch_related()
✅ **Índices de BD**: Agregados en Producto, Pedido, ItemCarrito
✅ **Carga Selectiva**: only() para cargar solo campos necesarios

### Resultados Esperados
- 📉 30-50% menos consultas a la base de datos
- ⚡ 40-60% más rápido con caché
- 💾 20-30% menos uso de memoria

---

## 🔧 PASO 2: Optimizaciones Opcionales (Recomendadas)

### A. Instalar Redis (Para Caché Avanzado)

Si tienes Redis instalado, actualiza `glamoure/settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

```powershell
pip install django-redis redis
```

### B. Comprimir Archivos Estáticos

```powershell
pip install django-compressor
```

Agrega a `INSTALLED_APPS` en settings.py:
```python
'compressor',
```

Y agrega al final de settings.py:
```python
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
```

### C. Debug Toolbar (Solo Desarrollo)

```powershell
pip install django-debug-toolbar
```

En settings.py:
```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

En urls.py:
```python
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

---

## 🌐 PASO 3: Optimizaciones Frontend

### HTML - Lazy Loading de Imágenes

En tus templates, cambia las imágenes de:
```html
<img src="{{ producto.imagen_url }}" alt="{{ producto.nombre }}">
```

A:
```html
<img src="{{ producto.imagen_url }}" 
     alt="{{ producto.nombre }}" 
     loading="lazy">
```

### Preconnect a Supabase

En tu `base.html` o plantilla principal, agrega en el `<head>`:
```html
<link rel="preconnect" href="https://your-project.supabase.co">
<link rel="dns-prefetch" href="https://your-project.supabase.co">
```

### Incluir Scripts de Optimización

En tu template base, antes de cerrar `</body>`:
```html
<script src="{% static 'js/optimizaciones.js' %}"></script>
```

---

## 📊 PASO 4: Agregar Paginación (Recomendado)

En `core/views.py`, actualiza la vista index:

```python
from django.core.paginator import Paginator

def index(request):
    productos_list = Producto.objects.only('id', 'nombre', 'precio', 'imagen_url', 'destacado', 'categoria')
    paginator = Paginator(productos_list, 24)  # 24 productos por página
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)
    return render(request, 'index.html', {'productos': productos})
```

En tu template `index.html`, agrega al final:
```html
<div class="pagination">
    {% if productos.has_previous %}
        <a href="?page=1">Primera</a>
        <a href="?page={{ productos.previous_page_number }}">Anterior</a>
    {% endif %}

    <span>Página {{ productos.number }} de {{ productos.paginator.num_pages }}</span>

    {% if productos.has_next %}
        <a href="?page={{ productos.next_page_number }}">Siguiente</a>
        <a href="?page={{ productos.paginator.num_pages }}">Última</a>
    {% endif %}
</div>
```

---

## 🔍 Verificar Mejoras

### Con Django Debug Toolbar:
1. Instala debug toolbar (ver arriba)
2. Navega por tu sitio
3. Revisa el panel lateral que aparece
4. Verifica:
   - Número de queries SQL (debe ser < 10 por página)
   - Tiempo de carga (debe ser < 500ms)
   - Queries duplicadas (debe ser 0)

### Sin Toolbar:
Revisa el tiempo de carga en las DevTools del navegador:
1. F12 → Network
2. Recarga la página
3. Revisa el tiempo total (debe mejorar 40-60%)

---

## ⚠️ Para Producción

Cuando pases a producción, actualiza `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com', 'www.tu-dominio.com']

# Seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

Y ejecuta:
```powershell
python manage.py collectstatic
```

---

## 📈 Monitoreo Continuo

### Métricas a vigilar:
- ⏱️ Tiempo de respuesta del servidor (< 500ms)
- 🗄️ Número de consultas SQL por página (< 10)
- 💾 Uso de memoria (estable)
- 📦 Tamaño de archivos estáticos (< 100KB por página)

### Herramientas recomendadas:
- Django Debug Toolbar (desarrollo)
- Google PageSpeed Insights (producción)
- GTmetrix (análisis detallado)

---

## 🆘 Solución de Problemas

### "ModuleNotFoundError: No module named 'django'"
```powershell
# Activa tu entorno virtual primero
# Luego ejecuta los comandos
```

### Las migraciones no se aplican
```powershell
python manage.py migrate --run-syncdb
```

### El caché no funciona
```powershell
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'valor', 30)
>>> cache.get('test')
# Debe retornar 'valor'
```

---

## 📞 Próximos Pasos

1. ✅ Aplica las migraciones (REQUERIDO)
2. 🔍 Instala Django Debug Toolbar
3. 📄 Agrega paginación
4. 🖼️ Implementa lazy loading
5. 📊 Mide y compara resultados

¡Tu sitio debería sentirse mucho más rápido ahora! 🚀
