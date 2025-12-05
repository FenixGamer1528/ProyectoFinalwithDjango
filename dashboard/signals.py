from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from carrito.models import Pedido, Producto
from core.models import Reporte, Incidencia
from dashboard.models import ActividadReciente

User = get_user_model()


@receiver(post_save, sender=User)
def registrar_actividad_usuario(sender, instance, created, **kwargs):
    """Registra cuando se crea un nuevo usuario"""
    if created:
        ActividadReciente.objects.create(
            tipo='registro',
            titulo='Nuevo usuario registrado',
            descripcion=f'{instance.username} se ha registrado en el sistema',
            usuario=instance,
            objeto_id=instance.id,
            objeto_tipo='Usuario'
        )


@receiver(post_save, sender=Pedido)
def registrar_actividad_pedido(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un pedido"""
    if created:
        ActividadReciente.objects.create(
            tipo='venta',
            titulo='Nuevo pedido realizado',
            descripcion=f'Pedido #{instance.id} - Total: ${instance.total}',
            usuario=instance.usuario if instance.usuario else None,
            objeto_id=instance.id,
            objeto_tipo='Pedido'
        )


@receiver(post_save, sender=Producto)
def registrar_actividad_producto(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un producto"""
    if created:
        ActividadReciente.objects.create(
            tipo='producto',
            titulo='Nuevo producto agregado',
            descripcion=f'{instance.nombre} ha sido agregado al inventario',
            usuario=None,
            objeto_id=instance.id,
            objeto_tipo='Producto'
        )
    else:
        # Verificar si el stock es bajo
        if hasattr(instance, 'stock') and instance.stock <= 10:
            ActividadReciente.objects.create(
                tipo='alerta',
                titulo='Alerta de stock bajo',
                descripcion=f'{instance.nombre} tiene solo {instance.stock} unidades disponibles',
                usuario=None,
                objeto_id=instance.id,
                objeto_tipo='Producto'
            )


@receiver(post_delete, sender=Producto)
def registrar_eliminacion_producto(sender, instance, **kwargs):
    """Registra cuando se elimina un producto"""
    ActividadReciente.objects.create(
        tipo='producto',
        titulo='Producto eliminado',
        descripcion=f'{instance.nombre} ha sido eliminado del sistema',
        usuario=None,
        objeto_id=instance.id,
        objeto_tipo='Producto'
    )


@receiver(post_save, sender=Reporte)
def registrar_actividad_reporte(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un reporte"""
    if created:
        ActividadReciente.objects.create(
            tipo='reporte',
            titulo='Nuevo reporte creado',
            descripcion=f'{instance.get_tipo_display()}: {instance.titulo}',
            usuario=instance.usuario,
            objeto_id=instance.id,
            objeto_tipo='Reporte'
        )
    elif instance.estado == 'resuelto':
        ActividadReciente.objects.create(
            tipo='reporte',
            titulo='Reporte resuelto',
            descripcion=f'{instance.titulo} ha sido marcado como resuelto',
            usuario=instance.responsable if instance.responsable else instance.usuario,
            objeto_id=instance.id,
            objeto_tipo='Reporte'
        )


@receiver(post_save, sender=Incidencia)
def registrar_actividad_incidencia(sender, instance, created, **kwargs):
    """Registra cuando se crea una incidencia"""
    if created:
        ActividadReciente.objects.create(
            tipo='incidencia',
            titulo='Nueva incidencia reportada',
            descripcion=f'{instance.get_tipo_display()}: {instance.descripcion[:50]}...',
            usuario=instance.reporte.usuario,
            objeto_id=instance.id,
            objeto_tipo='Incidencia'
        )
