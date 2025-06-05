from django.db import models



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

    

    
