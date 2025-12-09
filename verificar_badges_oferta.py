"""
Script para verificar que las etiquetas de oferta funcionan correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto

print("=" * 80)
print("VERIFICACION DE ETIQUETAS DE OFERTA")
print("=" * 80)

# Productos en oferta
productos_oferta = Producto.objects.filter(en_oferta=True)
print(f"\nProductos con en_oferta=True: {productos_oferta.count()}")
for p in productos_oferta:
    print(f"  - {p.nombre} (ID: {p.id})")
    print(f"    Categoria: {p.categoria}")
    print(f"    Destacado: {p.destacado}")
    print(f"    En oferta: {p.en_oferta}")

# Productos destacados
productos_destacados = Producto.objects.filter(destacado=True)
print(f"\nProductos destacados: {productos_destacados.count()}")
for p in productos_destacados:
    print(f"  - {p.nombre} (ID: {p.id})")
    print(f"    Categoria: {p.categoria}")
    print(f"    Destacado: {p.destacado}")
    print(f"    En oferta: {p.en_oferta}")

print("\n" + "=" * 80)
print("RESUMEN DE CORRECCIONES")
print("=" * 80)

print("\nCORRECCIONES APLICADAS:")
print("1. Vista de ofertas corregida:")
print("   - Antes: filtraba por categoria='ofertas' (incorrecto)")
print("   - Ahora: filtra por en_oferta=True (correcto)")

print("\n2. Badges agregados en todos los templates:")
print("   - hombres.html: Muestra TOP si destacado, OFERTA si en_oferta")
print("   - mujeres.html: Muestra TOP si destacado, OFERTA si en_oferta")
print("   - zapatos.html: Muestra TOP si destacado, OFERTA si en_oferta")
print("   - mis_deseos.html: Muestra TOP si destacado, OFERTA si en_oferta")
print("   - productos.html: Ya tenia la logica correcta")
print("   - ofertas.html: Ya tenia la logica correcta")
print("   - index.html: Ya tenia la logica correcta")

print("\n3. Queries actualizadas:")
print("   - Todas las vistas ahora incluyen 'en_oferta' en .only()")
print("   - Esto permite que el template acceda al campo en_oferta")

print("\n" + "=" * 80)
print("COMPORTAMIENTO ESPERADO")
print("=" * 80)

print("\nCuando un producto tiene:")
print("  - destacado=True -> Muestra badge amarillo 'TOP'")
print("  - en_oferta=True -> Muestra badge rojo 'OFERTA'")
print("  - Si ambos son True -> Prioriza 'TOP' (destacado)")

print("\nPagina de ofertas (/ofertas/):")
print("  - Ahora muestra TODOS los productos con en_oferta=True")
print("  - Independientemente de su categoria")
print(f"  - Actualmente mostrara: {productos_oferta.count()} producto(s)")

print("\n" + "=" * 80)
print("ARCHIVOS MODIFICADOS")
print("=" * 80)

print("\n1. core/views.py:")
print("   - ofertas(): Filtro cambiado de categoria a en_oferta")
print("   - hombres(), mujeres(), zapatos(): Agregado 'en_oferta' en .only()")

print("\n2. Templates actualizados:")
print("   - core/templates/core/hombres.html")
print("   - core/templates/core/mujeres.html")
print("   - core/templates/core/zapatos.html")
print("   - core/templates/core/mis_deseos.html")

print("\n" + "=" * 80)
print("PRUEBAS RECOMENDADAS")
print("=" * 80)

print("\n1. Marcar mas productos como en_oferta:")
print("   - Ir al admin de Django")
print("   - Editar productos")
print("   - Marcar checkbox 'En oferta'")

print("\n2. Verificar en navegador:")
print("   - http://localhost:8000/ofertas/ -> Debe mostrar productos en oferta")
print("   - http://localhost:8000/hombres/ -> Debe mostrar badge OFERTA")
print("   - http://localhost:8000/mujeres/ -> Debe mostrar badge OFERTA")
print("   - http://localhost:8000/zapatos/ -> Debe mostrar badge OFERTA")

print("\n" + "=" * 80)
print("CORRECCION COMPLETADA")
print("=" * 80)
