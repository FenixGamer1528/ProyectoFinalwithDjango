import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

# Buscar el vestido
vestido = Producto.objects.filter(nombre__icontains='Vestido con Falda').first()

if vestido:
    print(f'✅ Producto encontrado: {vestido.nombre}')
    print(f'   ID: {vestido.id}')
    print(f'   Categoría: {vestido.categoria}')
    print(f'   Imagen URL: {vestido.imagen_url or "Sin URL"}')
    print(f'   Imagen: {vestido.imagen or "Sin imagen"}')
    
    # Ver variantes
    variantes = ProductoVariante.objects.filter(producto=vestido)
    print(f'\n📦 Variantes encontradas: {variantes.count()}')
    print('-' * 80)
    
    for v in variantes:
        print(f'ID: {v.id}')
        print(f'  Talla: {v.talla}')
        print(f'  Color: {v.color}')
        print(f'  Stock: {v.stock}')
        print(f'  Imagen URL: {v.imagen_url or "❌ SIN IMAGEN"}')
        print(f'  Imagen: {v.imagen or "❌ SIN ARCHIVO"}')
        print(f'  IA: {v.imagen_generada_ia}')
        print('-' * 80)
else:
    print('❌ Producto no encontrado')

# Buscar botas para comparar
print('\n\n🥾 COMPARACIÓN - Botas Slouch:')
botas = Producto.objects.filter(nombre__icontains='Botas Slouch').first()

if botas:
    print(f'✅ Producto: {botas.nombre}')
    variantes_botas = ProductoVariante.objects.filter(producto=botas)
    print(f'📦 Variantes: {variantes_botas.count()}')
    for v in variantes_botas:
        print(f'  - {v.color} (Talla {v.talla}): {v.imagen_url or "❌ SIN IMAGEN"}')
