from django.contrib.auth.models import AbstractUser
from django.db import models

<<<<<<< HEAD


import datetime

class Usuario(models.Model):
    usuario = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario
    


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=250, default='', blank=True,null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='uploads/productos/')
    destacado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    

    
=======
class UsuarioPersonalizado(AbstractUser):
    telefono = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.username

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def _str_(self):
        return self.nombre

class Pedido(models.Model):
    UsuarioPersonalizado = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Pedido #{self.id} de {self.usuario}"
>>>>>>> 4a0f18c3d850a59a49289a69804614ac2703d9b7
