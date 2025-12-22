from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('checkout/', views.pagina_pago, name='checkout'),
    path('confirmacion/', views.confirmar_pago, name='confirmacion'),
    path('webhook/', views.webhook_wompi, name='webhook'),
    path('historial/', views.historial_transacciones, name='historial'),
    path('checkout-carrito/', views.checkout_desde_carrito, name='checkout_carrito'),
    path('confirmacion-carrito/', views.confirmar_pago_carrito, name='confirmacion_carrito'),
]
