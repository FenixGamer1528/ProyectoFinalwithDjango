from django.db import models
from django.conf import settings


class ActividadReciente(models.Model):
    """Modelo para registrar actividades recientes en el sistema"""
    
    TIPO_ACTIVIDAD = [
        ('usuario_registrado', 'Nuevo usuario registrado'),
        ('usuario_actualizado', 'Usuario actualizado'),
        ('pedido_creado', 'Pedido creado'),
        ('pedido_actualizado', 'Pedido actualizado'),
        ('pedido_completado', 'Pedido completado'),
        ('producto_creado', 'Producto creado'),
        ('producto_actualizado', 'Producto actualizado'),
        ('producto_eliminado', 'Producto eliminado'),
        ('reporte_creado', 'Reporte creado'),
        ('incidencia_creada', 'Incidencia creada'),
    ]
    
    tipo = models.CharField(max_length=50, choices=TIPO_ACTIVIDAD, verbose_name="Tipo de actividad")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                null=True, blank=True, verbose_name="Usuario")
    
    # Referencias opcionales
    objeto_id = models.IntegerField(null=True, blank=True, verbose_name="ID del objeto")
    objeto_tipo = models.CharField(max_length=50, null=True, blank=True, 
                                   verbose_name="Tipo de objeto")
    
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = "Actividad Reciente"
        verbose_name_plural = "Actividades Recientes"
    
    def __str__(self):
        return f"{self.titulo} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
    
    def get_icono(self):
        """Retorna el icono de FontAwesome según el tipo de actividad"""
        iconos = {
            'usuario_registrado': 'fa-user-plus',
            'usuario_actualizado': 'fa-user-edit',
            'pedido_creado': 'fa-shopping-cart',
            'pedido_actualizado': 'fa-edit',
            'pedido_completado': 'fa-check-circle',
            'producto_creado': 'fa-box',
            'producto_actualizado': 'fa-box-open',
            'producto_eliminado': 'fa-trash',
            'reporte_creado': 'fa-file-alt',
            'incidencia_creada': 'fa-exclamation-triangle',
        }
        return iconos.get(self.tipo, 'fa-bell')
    
    def tiempo_transcurrido(self):
        """Retorna el tiempo transcurrido de forma legible"""
        from django.utils import timezone
        from datetime import timedelta
        
        ahora = timezone.now()
        diferencia = ahora - self.fecha
        
        if diferencia < timedelta(minutes=1):
            return "Hace unos segundos"
        elif diferencia < timedelta(hours=1):
            minutos = int(diferencia.total_seconds() / 60)
            return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
        elif diferencia < timedelta(days=1):
            horas = int(diferencia.total_seconds() / 3600)
            return f"Hace {horas} hora{'s' if horas > 1 else ''}"
        elif diferencia < timedelta(days=7):
            dias = diferencia.days
            return f"Hace {dias} día{'s' if dias > 1 else ''}"
        else:
            return self.fecha.strftime("%d/%m/%Y, %H:%M")
