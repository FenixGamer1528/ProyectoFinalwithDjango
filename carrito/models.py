from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from decimal import Decimal

class Producto(models.Model):
    class CategoriaEnum(models.TextChoices):
        MUJER = 'mujer', 'Mujer'
        HOMBRE = 'hombre', 'Hombre'
        ZAPATOS = 'zapatos', 'Zapatos'
        OFERTAS = 'ofertas', 'Ofertas'

    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=250, default='', blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='uploads/productos/')
    destacado = models.BooleanField(default=False)
    stock = models.IntegerField(default=0)
    categoria = models.CharField(
        max_length=20,
        choices=CategoriaEnum.choices,
        default=CategoriaEnum.MUJER
    )

    def __str__(self):
        return self.nombre

class UsuarioPersonalizado(AbstractUser):
    telefono = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.username

# en models.py
class Pedido(models.Model):
    # 👇 Cambio aquí
    usuario = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE) 
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    # 👇 Y aquí
    def __str__(self):
        return f"Pedido #{self.id} de {self.usuario}"
    def _str_(self):
        return f"Pedido #{self.id} de {self.usuario}"
class Carrito(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        precio = self.producto.precio
        if isinstance(precio, Decimal):
            precio = self.producto.precio 
        return precio * self.cantidad