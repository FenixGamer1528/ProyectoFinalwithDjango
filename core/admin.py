from django.contrib import admin
from .models import Reporte, Incidencia, SeguimientoReporte, Categoria


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'tipo', 'categoria', 'estado', 'prioridad', 'asignado_a', 'fecha_creacion')
    list_filter = ('tipo', 'estado', 'prioridad', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion', 'categoria')
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'tipo', 'severidad', 'resuelto', 'reportado_por', 'fecha_reporte')
    list_filter = ('tipo', 'severidad', 'resuelto', 'fecha_reporte')
    search_fields = ('titulo', 'descripcion', 'producto_afectado')
    date_hierarchy = 'fecha_reporte'
    ordering = ('-fecha_reporte',)


@admin.register(SeguimientoReporte)
class SeguimientoReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporte', 'usuario', 'accion', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('accion', 'comentario')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

