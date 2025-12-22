import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

# Buscar el vestido
vestido = Producto.objects.get(id=138)

print(f'📦 Arreglando variantes de: {vestido.nombre}')
print(f'🖼️ Imagen del producto base: {vestido.imagen_url}')
print()

# Actualizar variantes sin imagen
variantes = ProductoVariante.objects.filter(producto=vestido)

for v in variantes:
    if not v.imagen_url and not v.imagen:
        # Asignar la imagen del producto base
        v.imagen_url = vestido.imagen_url
        v.save()
        print(f'✅ Actualizada variante {v.id}: {v.color} - Talla {v.talla}')
    else:
        print(f'⏭️ Variante {v.id} ya tiene imagen: {v.color} - Talla {v.talla}')

print()
print('🎉 ¡Listo! Ahora las variantes tienen imagen.')
print('🔄 Recarga la página con Ctrl+F5 para ver los cambios.')
