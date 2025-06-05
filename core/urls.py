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
<<<<<<< HEAD
    # path('registro/', views.registro_view, name='registro'),
=======
    path('registro/', views.registro_view, name='registro'),
    path('gestion_productos/', views.gestion_productos, name='gestion_productos'),
    path('gestion_pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
>>>>>>> 4a0f18c3d850a59a49289a69804614ac2703d9b7
]
