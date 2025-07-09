from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('index/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('registro/', views.registro_view, name='registro'),
    path('gestion_productos/', views.gestion_productos, name='gestion_productos'),
    path('gestion_pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
    path('lista_productos/', views.lista_productos, name='lista_productos'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('carrito/modal/', views.carrito_modal, name='carrito_modal'),
    path('producto/<int:product_id>/', views.producto, name='producto'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
]
