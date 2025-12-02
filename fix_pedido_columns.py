"""
Script para agregar manualmente las columnas faltantes en la tabla carrito_pedido
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from django.db import connection

def agregar_columnas_faltantes():
    with connection.cursor() as cursor:
        # Verificar qué columnas existen
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'carrito_pedido'
            ORDER BY ordinal_position;
        """)
        columnas_existentes = [row[0] for row in cursor.fetchall()]
        print("Columnas existentes:", columnas_existentes)
        
        # Agregar columna numero sin restricciones primero
        if 'numero' not in columnas_existentes:
            print("Agregando columna: numero")
            try:
                # Agregar sin UNIQUE ni DEFAULT primero
                cursor.execute("ALTER TABLE carrito_pedido ADD COLUMN numero VARCHAR(50);")
                print("✓ Columna numero agregada")
                
                # Generar valores únicos para cada pedido existente
                cursor.execute("""
                    UPDATE carrito_pedido 
                    SET numero = 'PED-' || TO_CHAR(fecha, 'YYYYMMDD') || '-' || UPPER(SUBSTRING(MD5(id::TEXT || RANDOM()::TEXT), 1, 8))
                    WHERE numero IS NULL;
                """)
                print(f"✓ {cursor.rowcount} pedidos con números generados")
                
                # Ahora agregar restricción NOT NULL
                cursor.execute("ALTER TABLE carrito_pedido ALTER COLUMN numero SET NOT NULL;")
                print("✓ Restricción NOT NULL agregada")
                
                # Agregar restricción UNIQUE
                cursor.execute("ALTER TABLE carrito_pedido ADD CONSTRAINT carrito_pedido_numero_key UNIQUE (numero);")
                print("✓ Restricción UNIQUE agregada")
                
            except Exception as e:
                print(f"✗ Error: {e}")
        else:
            print("○ Columna numero ya existe")
        
        # Lista de otras columnas
        otras_columnas = {
            'estado': "VARCHAR(20) NOT NULL DEFAULT 'pendiente'",
            'total': "NUMERIC(10, 2) NOT NULL DEFAULT 0",
            'direccion': "TEXT",
            'telefono': "VARCHAR(20)",
            'ciudad': "VARCHAR(100)",
            'codigo_postal': "VARCHAR(10)",
            'notas': "TEXT",
            'fecha_actualizacion': "TIMESTAMP WITH TIME ZONE"
        }
        
        # Agregar otras columnas faltantes
        for columna, tipo in otras_columnas.items():
            if columna not in columnas_existentes:
                print(f"Agregando columna: {columna}")
                try:
                    cursor.execute(f"ALTER TABLE carrito_pedido ADD COLUMN {columna} {tipo};")
                    print(f"✓ Columna {columna} agregada exitosamente")
                except Exception as e:
                    print(f"✗ Error agregando {columna}: {e}")
            else:
                print(f"○ Columna {columna} ya existe")
        
        # Crear índices si no existen
        print("\nCreando índices...")
        indices = [
            ("carrito_ped_estado_45ea2f_idx", "CREATE INDEX IF NOT EXISTS carrito_ped_estado_45ea2f_idx ON carrito_pedido (estado, fecha DESC);"),
            ("carrito_ped_numero_18691f_idx", "CREATE INDEX IF NOT EXISTS carrito_ped_numero_18691f_idx ON carrito_pedido (numero);"),
        ]
        
        for nombre_indice, sql in indices:
            try:
                cursor.execute(sql)
                print(f"✓ Índice {nombre_indice} creado")
            except Exception as e:
                print(f"○ Índice {nombre_indice}: {e}")
        
        # Verificar columnas finales
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'carrito_pedido'
            ORDER BY ordinal_position;
        """)
        columnas_finales = [row[0] for row in cursor.fetchall()]
        print("\nColumnas finales:", columnas_finales)

if __name__ == '__main__':
    print("Reparando estructura de tabla carrito_pedido...\n")
    agregar_columnas_faltantes()
    print("\n¡Reparación completada!")
