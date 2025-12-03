from django.contrib import admin
from dashboard.models import ActividadReciente


@admin.register(ActividadReciente)
class ActividadRecienteAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'titulo', 'usuario', 'fecha', 'get_icono']
    list_filter = ['tipo', 'fecha', 'objeto_tipo']
    search_fields = ['titulo', 'descripcion', 'usuario__username']
    date_hierarchy = 'fecha'
    readonly_fields = ['fecha']
    
    def get_icono(self, obj):
        return obj.get_icono()
    get_icono.short_description = 'Icono'
