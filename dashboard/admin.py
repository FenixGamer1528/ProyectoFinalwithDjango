from django.contrib import admin
from dashboard.models import ActividadReciente, ImagenColorCache


@admin.register(ImagenColorCache)
class ImagenColorCacheAdmin(admin.ModelAdmin):
    list_display = ['variante', 'color_hex', 'imagen_url_corta', 'fecha_generacion']
    list_filter = ['fecha_generacion', 'variante__producto__categoria']
    search_fields = ['variante__producto__nombre', 'color_hex']
    readonly_fields = ['fecha_generacion']
    date_hierarchy = 'fecha_generacion'
    
    def imagen_url_corta(self, obj):
        """Mostrar URL acortada en el admin"""
        if obj.imagen_url and len(obj.imagen_url) > 50:
            return f"{obj.imagen_url[:47]}..."
        return obj.imagen_url
    imagen_url_corta.short_description = 'URL Imagen'


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
