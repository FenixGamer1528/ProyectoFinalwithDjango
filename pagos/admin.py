from django.contrib import admin
from .models import Transaccion

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ['referencia', 'usuario', 'monto', 'estado', 'creado']
    list_filter = ['estado', 'creado', 'moneda']
    search_fields = ['referencia', 'wompi_transaction_id', 'email']
    readonly_fields = ['referencia', 'signature', 'creado', 'actualizado', 'respuesta_completa']
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'referencia', 'monto', 'moneda', 'estado')
        }),
        ('Datos de Wompi', {
            'fields': ('wompi_transaction_id', 'wompi_status', 'metodo_pago', 'signature')
        }),
        ('Información del Cliente', {
            'fields': ('email', 'nombre_completo')
        }),
        ('Datos Técnicos', {
            'fields': ('creado', 'actualizado', 'respuesta_completa'),
            'classes': ('collapse',)
        }),
    )