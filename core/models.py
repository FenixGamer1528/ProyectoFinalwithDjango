
from django.db import models
from django.conf import settings


class Reporte(models.Model):
    """Modelo para reportes de análisis de datos y problemas"""
    
    TIPOS = [
        ('problema', 'Problema/Incidencia'),
        ('analisis', 'Análisis de Datos'),
        ('auditoria', 'Auditoría'),
        ('ventas', 'Reporte de Ventas'),
        ('inventario', 'Inventario'),
        ('financiero', 'Financiero'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('revisando', 'En Revisión'),
        ('completado', 'Completado'),
        ('archivado', 'Archivado'),
    ]
    
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=200, verbose_name="Título")
    categoria = models.CharField(max_length=100, verbose_name="Categoría")
    tipo = models.CharField(max_length=20, choices=TIPOS, default='analisis', verbose_name="Tipo")
    descripcion = models.TextField(verbose_name="Descripción")
    
    # Gestión
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', verbose_name="Estado")
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='media', verbose_name="Prioridad")
    
    # Responsables
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='reportes_creados', verbose_name="Creado por")
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='reportes_asignados', verbose_name="Asignado a")
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    fecha_limite = models.DateField(null=True, blank=True, verbose_name="Fecha límite")
    fecha_completado = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de completado")
    
    # Análisis y soluciones
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    solucion = models.TextField(blank=True, verbose_name="Solución aplicada")
    
    # Metadatos para análisis
    datos_json = models.JSONField(null=True, blank=True, verbose_name="Datos del análisis")
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"


class Incidencia(models.Model):
    """Modelo para registrar problemas específicos (ej: falta de stock)"""
    
    TIPOS_INCIDENCIA = [
        ('stock', 'Falta de Stock'),
        ('calidad', 'Problema de Calidad'),
        ('logistica', 'Problema Logístico'),
        ('sistema', 'Error del Sistema'),
        ('cliente', 'Queja de Cliente'),
        ('otro', 'Otro'),
    ]
    
    SEVERIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=200, verbose_name="Título")
    tipo = models.CharField(max_length=20, choices=TIPOS_INCIDENCIA, verbose_name="Tipo de incidencia")
    descripcion = models.TextField(verbose_name="Descripción del problema")
    severidad = models.CharField(max_length=20, choices=SEVERIDADES, default='media', verbose_name="Severidad")
    
    # Relación con reporte
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name='incidencias',
                               null=True, blank=True, verbose_name="Reporte relacionado")
    
    # Gestión
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                     related_name='incidencias_reportadas', verbose_name="Reportado por")
    resuelto = models.BooleanField(default=False, verbose_name="Resuelto")
    solucion = models.TextField(blank=True, verbose_name="Solución")
    
    # Fechas
    fecha_reporte = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de reporte")
    fecha_resolucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de resolución")
    
    # Datos adicionales
    producto_afectado = models.CharField(max_length=200, blank=True, verbose_name="Producto afectado")
    cantidad_afectada = models.IntegerField(null=True, blank=True, verbose_name="Cantidad afectada")
    
    class Meta:
        ordering = ['-fecha_reporte']
        verbose_name = "Incidencia"
        verbose_name_plural = "Incidencias"
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"


class SeguimientoReporte(models.Model):
    """Modelo para registrar el historial de cambios en un reporte"""
    
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, 
                               related_name='seguimientos', verbose_name="Reporte")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Usuario")
    
    accion = models.CharField(max_length=100, verbose_name="Acción realizada")
    comentario = models.TextField(blank=True, verbose_name="Comentario")
    estado_anterior = models.CharField(max_length=20, blank=True, verbose_name="Estado anterior")
    estado_nuevo = models.CharField(max_length=20, blank=True, verbose_name="Estado nuevo")
    
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = "Seguimiento de Reporte"
        verbose_name_plural = "Seguimientos de Reportes"
    
    def __str__(self):
        return f"{self.reporte.titulo} - {self.accion}"

    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


