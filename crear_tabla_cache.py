import os
import django
import psycopg

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from django.conf import settings

# Obtener configuración de la base de datos
db_config = settings.DATABASES['default']

# Conectar a la base de datos
conn = psycopg.connect(
    dbname=db_config['NAME'],
    user=db_config['USER'],
    password=db_config['PASSWORD'],
    host=db_config['HOST'],
    port=db_config['PORT']
)

cursor = conn.cursor()

# SQL para crear la tabla
sql = """
CREATE TABLE IF NOT EXISTS dashboard_imagencolorcache (
    id SERIAL PRIMARY KEY,
    color_hex VARCHAR(7) NOT NULL,
    imagen_url VARCHAR(500) NOT NULL,
    fecha_generacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    variante_id INTEGER NOT NULL REFERENCES carrito_productovariante(id) ON DELETE CASCADE,
    UNIQUE (variante_id, color_hex)
);

CREATE INDEX IF NOT EXISTS dashboard_imagencolorcache_variante_id_idx ON dashboard_imagencolorcache(variante_id);
CREATE INDEX IF NOT EXISTS dashboard_imagencolorcache_fecha_generacion_idx ON dashboard_imagencolorcache(fecha_generacion DESC);
"""

try:
    cursor.execute(sql)
    conn.commit()
    print("✅ Tabla dashboard_imagencolorcache creada exitosamente")
    print("✅ Índices creados")
    
    # Verificar que la tabla existe
    cursor.execute("SELECT COUNT(*) FROM dashboard_imagencolorcache")
    count = cursor.fetchone()[0]
    print(f"✅ Tabla verificada: {count} registros")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
