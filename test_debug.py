from carrito.models import Producto, ProductoVariante

p = Producto.objects.get(id=105)
print('=== PRODUCTO BASE ===')
print(f'ID: {p.id}')
print(f'Nombre: {p.nombre}')
print(f'Talla: {p.talla}')
print(f'Colores: {p.colores}')

print('\n=== VARIANTES ===')
variantes = ProductoVariante.objects.filter(producto=p)
print(f'Total variantes: {variantes.count()}')

for v in variantes[:5]:
    print(f'Variante {v.id}: Talla={v.talla}, Color={v.color}')

# Simular la lógica de la vista
print('\n=== LÓGICA DE LA VISTA ===')
tallas_disponibles = []
if p.talla:
    tallas_disponibles.append(p.talla)
    print(f'Talla base agregada: {p.talla}')

for v in variantes:
    if v.talla and v.talla not in tallas_disponibles:
        tallas_disponibles.append(v.talla)
        print(f'Talla de variante agregada: {v.talla}')

colores_disponibles = []
if p.colores:
    colores_disponibles.append(p.colores)
    print(f'Color base agregado: {p.colores}')

for v in variantes:
    if v.color and v.color not in colores_disponibles:
        colores_disponibles.append(v.color)
        print(f'Color de variante agregado: {v.color}')

print('\n=== RESULTADO FINAL ===')
print(f'Tallas disponibles: {tallas_disponibles}')
print(f'Colores disponibles: {colores_disponibles}')
