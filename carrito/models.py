from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from decimal import Decimal
from datetime import datetime
import uuid
from core.utils.supabase_storage import subir_a_supabase
from django.utils import timezone
import random


class Producto(models.Model):
    class CategoriaEnum(models.TextChoices):
        MUJER = 'mujer', 'Mujer'
        HOMBRE = 'hombre', 'Hombre'
        ZAPATOS = 'zapatos', 'Zapatos'
        OFERTAS = 'ofertas', 'Ofertas'
        
    nombre = models.CharField(max_length=150)  # Índice creado manualmente
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    imagen_url = models.URLField(blank=True, null=True)
    # Talla opcional del producto (ej: S, M, L, 38, 39, etc.)
    talla = models.CharField(max_length=20, blank=True, null=True)
    en_oferta = models.BooleanField(default=False)
    colores = models.CharField(max_length=200, blank=True, null=True)
    destacado = models.BooleanField(default=False)  # Índice creado manualmente
    stock = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(
        max_length=20,
        choices=CategoriaEnum.choices,
        default=CategoriaEnum.MUJER
        # Índice creado manualmente para evitar conflictos con ENUM
    )

    class Meta:
        indexes = [
            models.Index(fields=['categoria', 'destacado']),  # Índice compuesto
            models.Index(fields=['-precio']),  # Para ordenar por precio
        ]
        ordering = ['-id']  # Orden por defecto

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
    def delete(self, *args, **kwargs):
        """Elimina la imagen del bucket de Supabase al eliminar el producto."""
        if self.imagen_url:
            try:
                from core.utils.supabase_storage import eliminar_de_supabase
                from urllib.parse import unquote, urlparse

                # Quitar parámetros o signos "?" de la URL
                ruta = urlparse(self.imagen_url).path  
                nombre_archivo = ruta.split("/storage/v1/object/public/media/")[-1].strip()
                nombre_archivo = unquote(nombre_archivo)

                # Eliminar barras iniciales si las hubiera
                if nombre_archivo.startswith("/"):
                    nombre_archivo = nombre_archivo[1:]

                print(f"🧩 Eliminando de Supabase: {nombre_archivo}")
                eliminar_de_supabase(nombre_archivo)

            except Exception as e:
                print(f"⚠️ No se pudo eliminar la imagen de Supabase: {e}")

        super().delete(*args, **kwargs)




class UsuarioPersonalizado(AbstractUser):
    telefono = models.CharField(max_length=15, blank=True)
    # Lista de deseos: productos que el usuario marcó como favorito
    favoritos = models.ManyToManyField('Producto', blank=True, related_name='favorited_by')

    def __str__(self):
        return self.username


class EstadoPedido(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    PROCESANDO = 'procesando', 'Procesando'
    COMPLETADO = 'completado', 'Completado'
    CANCELADO = 'cancelado', 'Cancelado'


class Pedido(models.Model):
    usuario = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE, related_name='pedidos')
    numero = models.CharField(max_length=50, unique=True, editable=False)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20,
        choices=EstadoPedido.choices,
        default=EstadoPedido.PENDIENTE,
        null=False,
        blank=False
    )
    
    # Información de envío
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    
    # Notas adicionales
    notas = models.TextField(blank=True, null=True)
    
    # Fechas
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['usuario', '-fecha']),
            models.Index(fields=['estado', '-fecha']),
            models.Index(fields=['numero']),
        ]
        ordering = ['-fecha']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def save(self, *args, **kwargs):
        # Asegurar que el estado tenga un valor
        if not self.estado:
            self.estado = EstadoPedido.PENDIENTE
        
        # Generar número de pedido único si no existe
        if not self.numero:
            self.numero = f"PED-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Calcular total si no está establecido o es cero
        if not self.total or self.total == Decimal('0'):
            self.total = self.producto.precio * self.cantidad
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido {self.numero} - {self.usuario.username}"
    
    @property
    def cliente(self):
        """Retorna el nombre completo del cliente"""
        return self.usuario.get_full_name() or self.usuario.username
    
    @property
    def email(self):
        """Retorna el email del cliente"""
        return self.usuario.email

class Carrito(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    # Guardamos la talla y color seleccionados por el usuario cuando agrega al carrito
    talla = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['carrito', 'producto']),  # Para búsquedas rápidas
        ]

    def subtotal(self):
        precio = self.producto.precio
        if isinstance(precio, Decimal):
            precio = self.producto.precio 
        return precio * self.cantidad


class TipoProducto(models.TextChoices):
    """Tipos de producto que determinan las tallas disponibles"""
    ROPA = 'ropa', 'Ropa (camisetas, buzos, camisas)'
    PANTALONES = 'pantalones', 'Pantalones'
    ZAPATOS = 'zapatos', 'Zapatos'


class ProductoVariante(models.Model):
    """
    Variante de un producto con talla, color e inventario independiente.
    Cada variante es una combinación única de producto + talla + color.
    """
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variantes')
    tipo_producto = models.CharField(
        max_length=20,
        choices=TipoProducto.choices,
        default=TipoProducto.ROPA
    )
    talla = models.CharField(max_length=10)  # Ej: S, M, L, 32, 38
    color = models.CharField(max_length=50)  # Ej: Negro, Rojo, Azul
    stock = models.IntegerField(default=0)
    # Imagen específica para esta variante (puede ser generada por IA)
    imagen = models.ImageField(upload_to='variantes/', blank=True, null=True)
    imagen_url = models.URLField(blank=True, null=True)
    # Indica si la imagen fue generada por IA
    imagen_generada_ia = models.BooleanField(default=False)
    
    class Meta:
        # Una combinación producto+talla+color debe ser única
        unique_together = ['producto', 'talla', 'color']
        indexes = [
            models.Index(fields=['producto', 'talla', 'color']),
            models.Index(fields=['stock']),
        ]
        ordering = ['talla', 'color']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.talla} - {self.color} (Stock: {self.stock})"
    
    def save(self, *args, **kwargs):
        """Similar al Producto, sube imagen a Supabase si existe"""
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
            print("Error subiendo imagen de variante a Supabase:", e)

        super().save(*args, **kwargs)


class Inventario(models.Model):
    """
    Registro de inventario por variante de producto.
    Permite rastrear entradas, salidas y stock actual.
    """
    TIPO_MOVIMIENTO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]
    
    variante = models.ForeignKey(ProductoVariante, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.IntegerField()
    stock_anterior = models.IntegerField()
    stock_nuevo = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    observaciones = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['variante', '-fecha']),
        ]
    
    def __str__(self):
        return f"{self.tipo_movimiento.upper()} - {self.variante} - {self.cantidad} unidades"