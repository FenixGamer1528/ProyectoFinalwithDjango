from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

    
urlpatterns = [
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('carrito/modal/', views.carrito_modal, name='carrito_modal'),
    path('producto/<int:product_id>/', views.producto, name='producto'),
    path('carrito/cambiar/<int:item_id>/<str:accion>/', views.cambiar_cantidad, name='cambiar_cantidad'),
    
   
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
