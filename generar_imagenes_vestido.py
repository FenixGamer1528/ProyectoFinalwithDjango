import os
import django
from PIL import Image, ImageEnhance
import requests
from io import BytesIO
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamoure.settings')
django.setup()

from carrito.models import Producto, ProductoVariante
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

print("=" * 80)
print("🎨 GENERANDO IMÁGENES DE COLORES PARA VESTIDO")
print("=" * 80)

def recolorizar_imagen(imagen_url, color_objetivo):
    """Recoloriza una imagen al color objetivo usando ajustes de tono"""
    print(f"\n📥 Descargando imagen: {imagen_url[:60]}...")
    
    # Descargar imagen
    response = requests.get(imagen_url)
    img = Image.open(BytesIO(response.content))
    
    # Convertir a RGB si es necesario
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    print(f"✅ Imagen descargada: {img.size}")
    
    # Aplicar filtro de color según el color objetivo
    if color_objetivo.lower() == 'negro':
        print("🎨 Aplicando filtro NEGRO...")
        # Reducir brillo y saturación para simular negro
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.4)  # Más oscuro
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.3)  # Menos saturación
        
    elif color_objetivo.lower() in ['marrón', 'marron']:
        print("🎨 Aplicando filtro MARRÓN...")
        # Ajustar hacia tonos cálidos/marrones
        pixels = img.load()
        width, height = img.size
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                # Aumentar rojo, reducir azul para tonos marrones
                r = min(255, int(r * 1.2))
                g = min(255, int(g * 0.9))
                b = min(255, int(b * 0.6))
                pixels[x, y] = (r, g, b)
        
        # Reducir un poco el brillo
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.85)
    
    print(f"✅ Filtro aplicado correctamente")
    return img

def subir_imagen(imagen_pil, color, producto_id):
    """Guarda la imagen usando el sistema de storage de Django"""
    print(f"\n📤 Guardando imagen {color}...")
    
    # Convertir PIL a bytes
    img_byte_arr = BytesIO()
    imagen_pil.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr.seek(0)
    
    try:
        # Generar nombre único
        nombre_archivo = f"productos/vestido_{color.lower().replace(' ', '_')}_{producto_id}_{uuid.uuid4().hex[:8]}.jpg"
        
        # Guardar usando el storage de Django (que ya está configurado con Supabase)
        path = default_storage.save(nombre_archivo, ContentFile(img_byte_arr.getvalue()))
        
        # Obtener URL completa
        url = default_storage.url(path)
        
        print(f"✅ Imagen guardada: {url[:60]}...")
        return url
        
    except Exception as e:
        print(f"❌ Error al guardar: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Obtener el vestido y sus variantes
vestido = Producto.objects.get(id=138)
variantes = ProductoVariante.objects.filter(producto=vestido)

print(f"\n📦 Producto: {vestido.nombre}")
print(f"🖼️ Imagen base: {vestido.imagen_url[:60]}...")
print(f"📊 Variantes a procesar: {variantes.count()}")

# Agrupar variantes por color
colores = {}
for v in variantes:
    if v.color not in colores:
        colores[v.color] = []
    colores[v.color].append(v)

print(f"\n🎨 Colores detectados: {list(colores.keys())}")

# Generar imagen para cada color
for color, vars_de_color in colores.items():
    print(f"\n{'='*60}")
    print(f"🎨 Procesando color: {color}")
    print(f"{'='*60}")
    
    # Generar imagen para cada color
    try:
        imagen_recolorizada = recolorizar_imagen(vestido.imagen_url, color)
        
        # Subir imagen
        url_nueva = subir_imagen(imagen_recolorizada, color, vestido.id)
        
        if url_nueva:
            # Actualizar todas las variantes de este color
            for variante in vars_de_color:
                variante.imagen_url = url_nueva
                variante.imagen_generada_ia = True
                variante.save()
                print(f"   ✅ Variante {variante.id} ({variante.talla}) actualizada")
        
    except Exception as e:
        print(f"❌ Error procesando {color}: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("🎉 ¡PROCESO COMPLETADO!")
print("=" * 80)
print("\n📋 RESUMEN:")
for color, vars_de_color in colores.items():
    v = vars_de_color[0]
    print(f"   {color}: {len(vars_de_color)} variantes")
    print(f"      URL: {v.imagen_url[:60] if v.imagen_url else 'ERROR'}...")
