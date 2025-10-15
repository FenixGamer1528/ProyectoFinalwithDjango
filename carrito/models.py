from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from decimal import Decimal
from core.utils.supabase_storage import subir_a_supabase

class Producto(models.Model):
    class CategoriaEnum(models.TextChoices):
        MUJER = 'mujer', 'Mujer'
        HOMBRE = 'hombre', 'Hombre'
        ZAPATOS = 'zapatos', 'Zapatos'
        OFERTAS = 'ofertas', 'Ofertas'
        
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    imagen_url = models.URLField(blank=True, null=True)
    destacado = models.BooleanField(default=False)
    stock = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(
        max_length=20,
        choices=CategoriaEnum.choices,
        default=CategoriaEnum.MUJER
    )

    def save(self, *args, **kwargs):
        """Si se sube una nueva imagen, la sube a Supabase y guarda su URL."""
        try:
            nueva_imagen = bool(self.imagen and getattr(self.imagen, "name", None))
            imagen_cambio = False

            if self.pk and nueva_imagen:
                try:
                    old = self.__class__.objects.get(pk=self.pk)
                    old_name = getattr(old.imagen, "name", None)
                    imagen_cambio = (old_name != self.imagen.name)
                except self.__class__.DoesNotExist:
                    imagen_cambio = True
            else:
                imagen_cambio = nueva_imagen and not self.imagen_url

            if nueva_imagen and imagen_cambio:
                url = subir_a_supabase(self.imagen)
                self.imagen_url = url
                try:
                    self.imagen.delete(save=False)
                except Exception:
                    pass
        except Exception as e:
            print("Error subiendo imagen a Supabase:", e)

        super().save(*args, **kwargs)

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