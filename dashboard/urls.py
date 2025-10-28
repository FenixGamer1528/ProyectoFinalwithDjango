from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),  

    path('usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    path('productos/', views.gestion_productos, name='gestion_productos'),
    path('pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    
    path('reportes/', views.gestion_reportes, name='gestion_reportes'),
   path('gestion/', views.gestion_productos, name='gestion_productos'),
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),
     path('cliente/', views.dashboardCliente, name='dashboard_cliente'),
]
