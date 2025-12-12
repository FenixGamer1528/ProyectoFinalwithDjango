"""
Script para probar la activación/desactivación de usuarios
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import UsuarioPersonalizado

# Listar usuarios y su estado
print("=" * 60)
print("USUARIOS EN EL SISTEMA:")
print("=" * 60)

usuarios = UsuarioPersonalizado.objects.all()

for usuario in usuarios:
    estado = "✅ ACTIVO" if usuario.is_active else "❌ INACTIVO"
    print(f"ID: {usuario.id} | Username: {usuario.username:20} | Estado: {estado}")

print("\n" + "=" * 60)
print("PRUEBA DE ACTIVAR/DESACTIVAR")
print("=" * 60)

# Obtener el primer usuario que no sea superusuario
usuario_prueba = UsuarioPersonalizado.objects.filter(is_superuser=False).first()

if usuario_prueba:
    print(f"\nUsuario seleccionado: {usuario_prueba.username}")
    print(f"Estado actual: {'ACTIVO' if usuario_prueba.is_active else 'INACTIVO'}")
    
    # Cambiar estado
    usuario_prueba.is_active = not usuario_prueba.is_active
    usuario_prueba.save()
    
    print(f"Nuevo estado: {'ACTIVO' if usuario_prueba.is_active else 'INACTIVO'}")
    print("✅ Cambio realizado con éxito")
    
    # Volver al estado original
    usuario_prueba.is_active = not usuario_prueba.is_active
    usuario_prueba.save()
    print(f"Estado restaurado a: {'ACTIVO' if usuario_prueba.is_active else 'INACTIVO'}")
else:
    print("❌ No hay usuarios disponibles para probar")

print("\n" + "=" * 60)
