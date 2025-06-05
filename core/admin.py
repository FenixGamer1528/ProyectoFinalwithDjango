from django.contrib import admin
from .models import Usuario,Producto

admin.site.register(Usuario)
admin.site.register(Producto)

# class ProductoAdmin(admin.ModelAdmin):
#     list_display = ('nombre', 'precio', 'destacado')
#     list_filter = ('destacado',)    
