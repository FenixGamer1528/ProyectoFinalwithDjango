# Generated manually for optimizations
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0008_alter_pedido_options_alter_producto_options_and_more'),
    ]

    operations = [
        # Crear índices usando SQL directo para evitar problemas con ENUMs
        migrations.RunSQL(
            # Forward SQL
            sql=[
                # Índice en nombre (solo si no existe)
                "CREATE INDEX IF NOT EXISTS carrito_producto_nombre_idx ON carrito_producto(nombre);",
                # Índice en destacado (solo si no existe)
                "CREATE INDEX IF NOT EXISTS carrito_producto_destacado_idx ON carrito_producto(destacado);",
                # Índice en categoria (solo si no existe)
                "CREATE INDEX IF NOT EXISTS carrito_producto_categoria_idx ON carrito_producto(categoria);",
                # Índice en fecha de pedido (solo si no existe)
                "CREATE INDEX IF NOT EXISTS carrito_pedido_fecha_idx ON carrito_pedido(fecha DESC);",
            ],
            # Reverse SQL
            reverse_sql=[
                "DROP INDEX IF EXISTS carrito_producto_nombre_idx;",
                "DROP INDEX IF EXISTS carrito_producto_destacado_idx;",
                "DROP INDEX IF EXISTS carrito_producto_categoria_idx;",
                "DROP INDEX IF EXISTS carrito_pedido_fecha_idx;",
            ],
        ),
    ]
