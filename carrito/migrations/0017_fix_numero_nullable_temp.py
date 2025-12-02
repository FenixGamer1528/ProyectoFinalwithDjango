# Generated manually to fix production issue
from django.db import migrations, models

def generar_numeros_faltantes(apps, schema_editor):
    """Genera números únicos para pedidos que no tienen numero"""
    Pedido = apps.get_model('carrito', 'Pedido')
    import uuid
    from datetime import datetime
    
    pedidos_sin_numero = Pedido.objects.filter(numero__isnull=True)
    for pedido in pedidos_sin_numero:
        pedido.numero = f"PED-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        pedido.save()
    
    print(f"✅ {pedidos_sin_numero.count()} pedidos actualizados con número")

class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0016_alter_pedido_numero'),
    ]

    operations = [
        # Primero hacer el campo nullable temporalmente
        migrations.AlterField(
            model_name='pedido',
            name='numero',
            field=models.CharField(max_length=50, unique=True, editable=False, null=True, blank=True),
        ),
        # Luego generar números para los que no tienen
        migrations.RunPython(generar_numeros_faltantes, migrations.RunPython.noop),
        # Finalmente volver a hacerlo NOT NULL
        migrations.AlterField(
            model_name='pedido',
            name='numero',
            field=models.CharField(max_length=50, unique=True, editable=False),
        ),
    ]
