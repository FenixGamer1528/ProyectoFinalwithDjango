"""
Script de prueba de rendimiento para validar optimizaciones
Ejecutar: python test_rendimiento.py
"""
import time
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from django.db import connection, reset_queries
from django.core.cache import cache
from carrito.models import Producto, Pedido
from core.models import Reporte

def medir_tiempo(func):
    """Decorador para medir tiempo de ejecución"""
    def wrapper(*args, **kwargs):
        reset_queries()
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        tiempo = fin - inicio
        queries = len(connection.queries)
        print(f"⏱️  {func.__name__}: {tiempo:.4f}s | Queries: {queries}")
        return resultado
    return wrapper

@medir_tiempo
def test_productos_optimizado():
    """Test: Cargar productos con optimización"""
    productos = Producto.objects.all().only(
        'id', 'nombre', 'precio', 'imagen_url', 'categoria'
    )[:20]
    return list(productos)

@medir_tiempo
def test_productos_sin_optimizar():
    """Test: Cargar productos sin optimización"""
    productos = Producto.objects.all()[:20]
    return list(productos)

@medir_tiempo
def test_productos_destacados_con_cache():
    """Test: Productos destacados con caché"""
    cache_key = 'test_productos_destacados'
    productos = cache.get(cache_key)
    if productos is None:
        productos = list(Producto.objects.filter(destacado=True).only(
            'id', 'nombre', 'precio', 'imagen_url'
        )[:10])
        cache.set(cache_key, productos, 300)
    return productos

@medir_tiempo
def test_productos_destacados_sin_cache():
    """Test: Productos destacados sin caché"""
    productos = list(Producto.objects.filter(destacado=True).only(
        'id', 'nombre', 'precio', 'imagen_url'
    )[:10])
    return productos

@medir_tiempo
def test_busqueda_optimizada():
    """Test: Búsqueda optimizada con límite"""
    productos = Producto.objects.filter(
        nombre__icontains='chaqueta'
    ).only('id', 'nombre', 'precio')[:50]
    return list(productos)

@medir_tiempo
def test_busqueda_sin_optimizar():
    """Test: Búsqueda sin optimización"""
    productos = Producto.objects.filter(
        nombre__icontains='chaqueta'
    )
    return list(productos)

def run_tests():
    """Ejecutar todas las pruebas de rendimiento"""
    print("\n" + "="*60)
    print("🚀 PRUEBAS DE RENDIMIENTO - GLAMOURE")
    print("="*60 + "\n")
    
    # Limpiar caché antes de empezar
    cache.clear()
    
    print("📦 Test 1: Carga de Productos")
    print("-" * 60)
    test_productos_optimizado()
    test_productos_sin_optimizar()
    print()
    
    print("⭐ Test 2: Productos Destacados (con vs sin caché)")
    print("-" * 60)
    # Primera llamada (sin caché)
    test_productos_destacados_con_cache()
    # Segunda llamada (con caché)
    print("🔄 Segunda llamada (debería ser más rápida):")
    test_productos_destacados_con_cache()
    # Sin caché para comparar
    test_productos_destacados_sin_cache()
    print()
    
    print("🔍 Test 3: Búsqueda de Productos")
    print("-" * 60)
    test_busqueda_optimizada()
    test_busqueda_sin_optimizar()
    print()
    
    # Estadísticas generales
    print("="*60)
    print("📊 ESTADÍSTICAS GENERALES")
    print("="*60)
    print(f"Total de productos: {Producto.objects.count()}")
    print(f"Productos destacados: {Producto.objects.filter(destacado=True).count()}")
    print(f"Productos en oferta: {Producto.objects.filter(en_oferta=True).count()}")
    print(f"Total de pedidos: {Pedido.objects.count()}")
    print()
    
    print("="*60)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)
    print("\n💡 Interpretación:")
    print("  - Las queries optimizadas deberían tener MENOS consultas SQL")
    print("  - El caché debería reducir el tiempo en ~80-90% en la 2da llamada")
    print("  - Las búsquedas con límite deberían ser más rápidas")
    print()

if __name__ == '__main__':
    run_tests()
