from django.contrib import admin
<<<<<<< HEAD
from .models import Usuario,Producto

admin.site.register(Usuario)
admin.site.register(Producto)

# class ProductoAdmin(admin.ModelAdmin):
#     list_display = ('nombre', 'precio', 'destacado')
#     list_filter = ('destacado',)    
=======
from .models import UsuarioPersonalizado
admin.site.register(UsuarioPersonalizado)
>>>>>>> 4a0f18c3d850a59a49289a69804614ac2703d9b7
