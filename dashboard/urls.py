from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),  

    path('usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    path('productos/', views.gestion_productos, name='gestion_productos'),
    
    # Gestión de pedidos
    path('pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
    path('pedidos/<int:pedido_id>/detalle/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/<int:pedido_id>/actualizar-estado/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
    path('pedidos/<int:pedido_id>/actualizar/', views.actualizar_pedido, name='actualizar_pedido'),
    path('pedidos/<int:pedido_id>/eliminar/', views.eliminar_pedido, name='eliminar_pedido'),
    
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    
    path('reportes/', views.gestion_reportes, name='gestion_reportes'),
    path('gestion/', views.gestion_productos, name='gestion_productos'),
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('cliente/', views.dashboardCliente, name='dashboard_cliente'),
    
    # Gestión de variantes
    path('producto/<int:producto_id>/variantes/', views.gestionar_variantes, name='gestionar_variantes'),
    path('variante/<int:variante_id>/editar/', views.editar_variante, name='editar_variante'),
    path('variante/<int:variante_id>/eliminar/', views.eliminar_variante, name='eliminar_variante'),
    
    # Gestión de inventario
    path('variante/<int:variante_id>/inventario/', views.historial_inventario, name='historial_inventario'),
    path('variante/<int:variante_id>/ajustar/', views.ajustar_inventario, name='ajustar_inventario'),
    
    # APIs
    path('api/producto/<int:producto_id>/variantes/', views.obtener_variantes_producto, name='api_variantes_producto'),
    path('api/producto/<int:producto_id>/detalle/', views.obtener_producto_detalle, name='api_producto_detalle'),
    path('api/variante/<int:variante_id>/generar-color/', views.generar_imagen_color, name='generar_imagen_color'),
    path('api/inventario/completo/', views.obtener_inventario_completo, name='api_inventario_completo'),
]