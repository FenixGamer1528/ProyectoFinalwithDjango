from django.contrib import admin
from .models import UsuarioPersonalizado,Producto,Carrito, ItemCarrito

admin.site.register(UsuarioPersonalizado)
admin.site.register(Producto)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
