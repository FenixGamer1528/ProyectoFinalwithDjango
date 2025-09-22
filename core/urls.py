from django.urls import path
from . import views
from .views import ReporteListView, exportar_excel, exportar_pdf
from django.conf import settings
from django.conf.urls.static import static

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
    path('reportes/', ReporteListView.as_view(), name='lista_reportes'),
    path('reportes/exportar/excel/', exportar_excel, name='exportar_excel'),
    path('reportes/exportar/pdf/', exportar_pdf, name='exportar_pdf'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
