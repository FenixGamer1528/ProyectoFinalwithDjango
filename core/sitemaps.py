from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from carrito.models import Producto

class StaticViewSitemap(Sitemap):
    """Sitemap para páginas estáticas"""
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['index', 'hombres', 'mujeres', 'zapatos', 'ofertas', 'catalogo_completo']

    def location(self, item):
        return reverse(item)


class ProductoSitemap(Sitemap):
    """Sitemap para productos"""
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Producto.objects.all()

    def lastmod(self, obj):
        # Si tienes un campo de fecha de modificación, úsalo aquí
        return None

    def location(self, obj):
        return reverse('producto', args=[obj.id])
