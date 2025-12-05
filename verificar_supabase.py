"""
Script para verificar la conexión y configuración de Supabase
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')

import django
django.setup()

from core.utils.supabase_storage import USE_SUPABASE, supabase, SUPABASE_URL, SUPABASE_KEY

print("=" * 80)
print("VERIFICACION DE CONFIGURACION DE SUPABASE")
print("=" * 80)

print(f"\nUSE_SUPABASE: {USE_SUPABASE}")

if USE_SUPABASE:
    print(f"\nSUPABASE_URL: {SUPABASE_URL[:50]}..." if SUPABASE_URL else "\nSUPABASE_URL: None")
    print(f"SUPABASE_KEY: {SUPABASE_KEY[:50]}..." if SUPABASE_KEY else "SUPABASE_KEY: None")
    print(f"Cliente Supabase inicializado: {'Si' if supabase else 'No'}")
    
    if supabase:
        try:
            # Intentar listar archivos en el bucket
            print("\nIntentando conectar al bucket 'media'...")
            result = supabase.storage.from_("media").list()
            print(f"Conexion exitosa! Archivos en bucket: {len(result)}")
            
            # Mostrar algunos archivos
            if result:
                print("\nPrimeros archivos en el bucket:")
                for i, archivo in enumerate(result[:5], 1):
                    print(f"  {i}. {archivo.get('name', 'sin nombre')}")
        except Exception as e:
            print(f"\nError al conectar con Supabase: {e}")
    else:
        print("\nNo se pudo inicializar el cliente de Supabase")
        print("Verifica las credenciales en el archivo .env")
else:
    print("\nSupabase esta DESHABILITADO")
    print("Cambia USE_SUPABASE = True en core/utils/supabase_storage.py")

print("\n" + "=" * 80)
print("ESTADO DE LA BASE DE DATOS")
print("=" * 80)

from carrito.models import Producto

productos = Producto.objects.all()
print(f"\nTotal de productos: {productos.count()}")

for p in productos:
    print(f"\nProducto: {p.nombre} (ID: {p.id})")
    print(f"  imagen_url: {p.imagen_url or 'None'}")
    print(f"  imagen (local): {p.imagen.name if p.imagen else 'None'}")
    
    if p.imagen_url:
        print(f"  Usando Supabase")
    elif p.imagen:
        print(f"  Usando almacenamiento local: /media/{p.imagen.name}")
    else:
        print(f"  Sin imagen")

print("\n" + "=" * 80)
print("INSTRUCCIONES")
print("=" * 80)

if USE_SUPABASE and supabase:
    print("\nSupabase esta HABILITADO y CONECTADO correctamente")
    print("\nCuando subas una nueva imagen desde el dashboard:")
    print("  1. La imagen se subira automaticamente a Supabase")
    print("  2. Se guardara en el bucket 'media'")
    print("  3. El campo imagen_url se actualizara con la URL publica")
    print("  4. La imagen local se eliminara (si existia)")
    print("\nPuedes probar creando o editando un producto en:")
    print("  http://localhost:8000/dashboard/productos/")
else:
    print("\nSupabase NO esta funcionando correctamente")
    print("\nPara habilitar Supabase:")
    print("  1. Verifica que USE_SUPABASE = True en core/utils/supabase_storage.py")
    print("  2. Verifica que exista el archivo .env con SUPABASE_URL y SUPABASE_KEY")
    print("  3. Reinicia el servidor de Django")
