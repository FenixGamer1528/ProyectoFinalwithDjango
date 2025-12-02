"""
Script para reparar la base de datos en producción
Ejecutar en el servidor: python fix_production_db.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from django.db import connection

def reparar_base_datos_produccion():
    """Repara la tabla carrito_pedido en producción"""
    with connection.cursor() as cursor:
        print("="*60)
        print("🔧 REPARANDO BASE DE DATOS EN PRODUCCIÓN")
        print("="*60)
        
        # 1. Verificar columnas existentes
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'carrito_pedido'
            ORDER BY ordinal_position;
        """)
        columnas_existentes = [row[0] for row in cursor.fetchall()]
        print(f"\n📋 Columnas existentes: {', '.join(columnas_existentes)}")
        
        # 2. Si la columna numero no existe, crearla
        if 'numero' not in columnas_existentes:
            print("\n❌ Columna 'numero' no existe. Creándola...")
            
            try:
                # Agregar columna sin restricciones
                cursor.execute("ALTER TABLE carrito_pedido ADD COLUMN numero VARCHAR(50);")
                print("✅ Columna 'numero' agregada")
                
                # Generar números únicos para pedidos existentes
                cursor.execute("""
                    UPDATE carrito_pedido 
                    SET numero = 'PED-' || TO_CHAR(fecha, 'YYYYMMDD') || '-' || UPPER(SUBSTRING(MD5(id::TEXT || RANDOM()::TEXT), 1, 8))
                    WHERE numero IS NULL;
                """)
                print(f"✅ {cursor.rowcount} pedidos actualizados con números únicos")
                
                # Agregar restricciones
                cursor.execute("ALTER TABLE carrito_pedido ALTER COLUMN numero SET NOT NULL;")
                cursor.execute("ALTER TABLE carrito_pedido ADD CONSTRAINT carrito_pedido_numero_key UNIQUE (numero);")
                print("✅ Restricciones agregadas (NOT NULL y UNIQUE)")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
        else:
            print("\n✅ Columna 'numero' ya existe")
            
            # Verificar si hay valores NULL
            cursor.execute("SELECT COUNT(*) FROM carrito_pedido WHERE numero IS NULL;")
            count_null = cursor.fetchone()[0]
            
            if count_null > 0:
                print(f"\n⚠️  Hay {count_null} pedidos con numero NULL. Actualizando...")
                cursor.execute("""
                    UPDATE carrito_pedido 
                    SET numero = 'PED-' || TO_CHAR(fecha, 'YYYYMMDD') || '-' || UPPER(SUBSTRING(MD5(id::TEXT || RANDOM()::TEXT), 1, 8))
                    WHERE numero IS NULL;
                """)
                print(f"✅ {cursor.rowcount} pedidos actualizados")
        
        # 3. Verificar índices
        print("\n📊 Verificando índices...")
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'carrito_pedido' AND indexname LIKE '%numero%';
        """)
        indices = [row[0] for row in cursor.fetchall()]
        
        if not any('numero' in idx for idx in indices):
            print("Creando índice para columna numero...")
            cursor.execute("CREATE INDEX IF NOT EXISTS carrito_ped_numero_18691f_idx ON carrito_pedido (numero);")
            print("✅ Índice creado")
        else:
            print(f"✅ Índice ya existe: {indices}")
        
        # 4. Estadísticas finales
        cursor.execute("SELECT COUNT(*) FROM carrito_pedido;")
        total_pedidos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM carrito_pedido WHERE numero IS NOT NULL AND numero != '';")
        pedidos_con_numero = cursor.fetchone()[0]
        
        print("\n" + "="*60)
        print("📈 ESTADÍSTICAS FINALES")
        print("="*60)
        print(f"Total de pedidos: {total_pedidos}")
        print(f"Pedidos con número: {pedidos_con_numero}")
        print(f"Estado: {'✅ OK' if total_pedidos == pedidos_con_numero else '❌ ERROR'}")
        print("="*60)
        
        return True

if __name__ == '__main__':
    try:
        exito = reparar_base_datos_produccion()
        if exito:
            print("\n🎉 ¡REPARACIÓN COMPLETADA EXITOSAMENTE!")
            print("\nAhora ejecuta:")
            print("  python manage.py migrate carrito --fake")
            print("  sudo systemctl restart gunicorn  # o tu comando de reinicio")
        else:
            print("\n❌ La reparación falló. Revisa los errores arriba.")
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
