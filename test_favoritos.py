from carrito.models import UsuarioPersonalizado, Producto

# Obtener el primer usuario y producto
usuario = UsuarioPersonalizado.objects.first()
producto = Producto.objects.first()

print(f"Usuario: {usuario.usuario if usuario else 'No hay usuarios'}")
print(f"Producto: {producto.nombre if producto else 'No hay productos'}")

if usuario and producto:
    # Agregar a favoritos
    usuario.favoritos.add(producto)
    print(f"\n✅ Producto agregado a favoritos")
    print(f"Total de favoritos: {usuario.favoritos.count()}")
    print(f"Productos en favoritos:")
    for fav in usuario.favoritos.all():
        print(f"  - {fav.nombre}")
    
    # Verificar si está en favoritos
    if producto in usuario.favoritos.all():
        print(f"\n✅ Verificación exitosa: {producto.nombre} está en favoritos")
    
    # Eliminar de favoritos
    usuario.favoritos.remove(producto)
    print(f"\n✅ Producto eliminado de favoritos")
    print(f"Total de favoritos: {usuario.favoritos.count()}")
else:
    print("❌ No hay datos para probar")
