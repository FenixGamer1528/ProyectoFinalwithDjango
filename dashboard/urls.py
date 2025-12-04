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
    
    # Gestión de reportes
    path('reportes/', views.gestion_reportes, name='gestion_reportes'),
    path('reportes/crear/', views.crear_reporte, name='crear_reporte'),
    path('reportes/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
    path('reportes/<int:reporte_id>/actualizar-estado/', views.actualizar_estado_reporte, name='actualizar_estado_reporte'),
    path('reportes/<int:reporte_id>/asignar-responsable/', views.asignar_responsable_reporte, name='asignar_responsable_reporte'),
    
    # Gestión de incidencias
    path('incidencias/crear/', views.crear_incidencia, name='crear_incidencia'),
    path('incidencias/crear/<int:reporte_id>/', views.crear_incidencia, name='crear_incidencia_reporte'),
    
    # Análisis de datos
    path('analisis/ventas/', views.analizar_ventas, name='analizar_ventas'),
    path('analisis/ventas/exportar/', views.exportar_reporte_ventas, name='exportar_reporte_ventas'),
    path('analisis/inventario/', views.analizar_inventario, name='analizar_inventario'),
    path('analisis/inventario/exportar/', views.exportar_reporte_inventario, name='exportar_reporte_inventario'),
    path('analisis/detectar-problemas/', views.detectar_problemas_automatico, name='detectar_problemas_automatico'),
    
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