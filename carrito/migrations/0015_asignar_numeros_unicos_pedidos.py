# Generated manually for data migration

from django.db import migrations
import uuid
from datetime import datetime


def asignar_numeros_unicos(apps, schema_editor):
    """Asignar números únicos a todos los pedidos existentes"""
    Pedido = apps.get_model('carrito', 'Pedido')
    
    for index, pedido in enumerate(Pedido.objects.all(), start=1):
        # Generar número único para cada pedido
        fecha_base = pedido.fecha if hasattr(pedido, 'fecha') and pedido.fecha else datetime.now()
        pedido.numero = f"PED-{fecha_base.strftime('%Y%m%d')}-{str(index).zfill(4)}"
        pedido.save(update_fields=['numero'])


def reverse_func(apps, schema_editor):
    """Función de reversión (no hace nada)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0014_alter_pedido_options_pedido_ciudad_and_more'),
    ]

    operations = [
        migrations.RunPython(asignar_numeros_unicos, reverse_func),
    ]
