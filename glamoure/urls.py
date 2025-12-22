from django.contrib import admin
from django.urls import path,include
from . import settings
from django.conf.urls.static import static
from core import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, ProductoSitemap

# Configuración de sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'productos': ProductoSitemap,
}

urlpatterns = [
   
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('carrito/', include('carrito.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('carrito.urls')),
    path('pagos/', include('pagos.urls')),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html',email_template_name='password_reset_email.html',subject_template_name='password_reset_subject.txt'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    # SEO URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
