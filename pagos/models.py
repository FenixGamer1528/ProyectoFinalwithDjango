from django.db import models
from django.conf import settings
import json

class Transaccion(models.Model):
    ESTADOS = [
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobada'),
        ('DECLINED', 'Rechazada'),
        ('VOIDED', 'Anulada'),
        ('ERROR', 'Error'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    referencia = models.CharField(max_length=100, unique=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, default='COP')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDING')
    
    # Datos de Wompi
    wompi_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    wompi_status = models.CharField(max_length=50, blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    
    # Datos del cliente
    email = models.EmailField(blank=True, null=True)
    nombre_completo = models.CharField(max_length=200, blank=True, null=True)
    
    # 🆕 NUEVO: Datos del pedido (productos del carrito)
    detalle_pedido = models.JSONField(blank=True, null=True)
    
    # Firma de integridad
    signature = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    # Respuesta completa de Wompi (JSON)
    respuesta_completa = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-creado']
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
    
    def __str__(self):
        return f"{self.referencia} - {self.get_estado_display()}"
    
    def get_productos(self):
        """Devuelve la lista de productos del pedido"""
        if self.detalle_pedido:
            return self.detalle_pedido.get('productos', [])
        return []
    
    def get_total_productos(self):
        """Devuelve el número total de productos"""
        if self.detalle_pedido:
            return sum(p['cantidad'] for p in self.detalle_pedido.get('productos', []))
        return 0