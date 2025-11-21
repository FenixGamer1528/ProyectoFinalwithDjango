from django.urls import path, include
from . import views
from .views import ReporteListView, exportar_excel, exportar_pdf
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('registro/', views.registro_view, name='registro'),
    path('gestion_productos/', views.gestion_productos, name='gestion_productos'),
    path('reportes/', ReporteListView.as_view(), name='lista_reportes'),
    path('reportes/exportar/excel/', exportar_excel, name='exportar_excel'),
    path('reportes/exportar/pdf/', exportar_pdf, name='exportar_pdf'),
    path('hombres/', views.hombres, name='hombres'),
    path('mujeres/', views.mujeres, name='mujeres'),
    path('zapatos/', views.zapatos, name='zapatos'),
    path('ofertas/', views.ofertas, name='ofertas'),
    path('toggle-favorito/<int:producto_id>/', views.toggle_favorito, name='toggle_favorito'),
    path('mis-deseos/', views.mis_deseos, name='mis_deseos'),
  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
