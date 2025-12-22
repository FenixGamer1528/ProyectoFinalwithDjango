import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante

# Buscar el producto corset
producto = Producto.objects.filter(nombre__icontains='corset').first()

if not producto:
    print("❌ Producto 'corset' no encontrado")
    print("\nProductos disponibles:")
    for p in Producto.objects.all()[:10]:
        print(f"  - ID: {p.id}, Nombre: {p.nombre}")
else:
    print(f"✅ Producto encontrado: {producto.nombre} (ID: {producto.id})")
    
    # Crear variante Rojo - Talla M
    variante, created = ProductoVariante.objects.get_or_create(
        producto=producto,
        talla='M',
        color='Rojo',
        defaults={
            'stock': 10,
            'tipo_producto': 'ropa',
            'imagen_url': producto.imagen_url if hasattr(producto, 'imagen_url') else None,
        }
    )
    
    if created:
        print(f"✅ Variante creada: {variante.producto.nombre} - {variante.color} - Talla {variante.talla}")
        print(f"   ID Variante: {variante.id}")
        print(f"   Stock: {variante.stock}")
    else:
        print(f"⚠️ La variante ya existía: ID {variante.id}")
    
    # Crear variante Negro - Talla M
    variante2, created2 = ProductoVariante.objects.get_or_create(
        producto=producto,
        talla='M',
        color='Negro',
        defaults={
            'stock': 8,
            'tipo_producto': 'ropa',
            'imagen_url': producto.imagen_url if hasattr(producto, 'imagen_url') else None,
        }
    )
    
    if created2:
        print(f"✅ Variante creada: {variante2.producto.nombre} - {variante2.color} - Talla {variante2.talla}")
        print(f"   ID Variante: {variante2.id}")
    else:
        print(f"⚠️ La variante ya existía: ID {variante2.id}")
    
    # Crear variante Blanco - Talla M
    variante3, created3 = ProductoVariante.objects.get_or_create(
        producto=producto,
        talla='M',
        color='Blanco',
        defaults={
            'stock': 12,
            'tipo_producto': 'ropa',
            'imagen_url': producto.imagen_url if hasattr(producto, 'imagen_url') else None,
        }
    )
    
    if created3:
        print(f"✅ Variante creada: {variante3.producto.nombre} - {variante3.color} - Talla {variante3.talla}")
        print(f"   ID Variante: {variante3.id}")
    else:
        print(f"⚠️ La variante ya existía: ID {variante3.id}")
    
    print(f"\n🎨 Total variantes del producto: {ProductoVariante.objects.filter(producto=producto).count()}")
    print("\nVariantes creadas:")
    for v in ProductoVariante.objects.filter(producto=producto):
        print(f"  - {v.color} (Talla {v.talla}) - Stock: {v.stock} - ID: {v.id}")
