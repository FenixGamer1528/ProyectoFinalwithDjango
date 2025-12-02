from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0009_add_manual_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='colores',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
