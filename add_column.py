import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Verificar si la columna existe en PostgreSQL
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='carrito_producto' AND column_name='en_oferta'
    """)
    
    result = cursor.fetchone()
    
    if not result:
        print("Agregando columna en_oferta...")
        cursor.execute("ALTER TABLE carrito_producto ADD COLUMN en_oferta BOOLEAN DEFAULT FALSE")
        print("✅ Columna en_oferta agregada exitosamente")
    else:
        print("✅ La columna en_oferta ya existe")
