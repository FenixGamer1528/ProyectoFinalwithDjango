"""
Comando de Django para generar automáticamente imágenes con IA para variantes de productos.

Uso:
    python manage.py generar_imagenes_ia                    # Procesar todas las variantes sin imagen
    python manage.py generar_imagenes_ia --producto-id 123  # Solo variantes del producto 123
    python manage.py generar_imagenes_ia --force            # Regenerar todas las imágenes
    python manage.py generar_imagenes_ia --color rojo       # Solo variantes de color rojo
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from carrito.models import ProductoVariante, Producto
from dashboard.models import ImagenColorCache
from dashboard.sam_recolor import process_image_recolor, SamUnavailableError
from dashboard.views import _detectar_categoria_producto
from core.utils.supabase_storage import subir_a_supabase
from PIL import Image
from django.core.files.base import ContentFile
import io
import requests
import os


class Command(BaseCommand):
    help = 'Genera imágenes con IA para variantes de productos que no tienen imagen propia'

    def add_arguments(self, parser):
        parser.add_argument(
            '--producto-id',
            type=int,
            help='ID del producto específico a procesar',
        )
        parser.add_argument(
            '--color',
            type=str,
            help='Procesar solo variantes de un color específico',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerar imágenes incluso si ya existen',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limitar número de variantes a procesar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎨 Iniciando generación de imágenes con IA...'))
        
        # Construir query
        query = Q()
        
        if options['producto_id']:
            query &= Q(producto_id=options['producto_id'])
            self.stdout.write(f"📦 Filtrando por producto ID: {options['producto_id']}")
        
        if options['color']:
            query &= Q(color__icontains=options['color'])
            self.stdout.write(f"🎨 Filtrando por color: {options['color']}")
        
        if not options['force']:
            # Solo procesar variantes sin imagen propia
            query &= Q(imagen='') & Q(imagen_url__isnull=True)
            self.stdout.write("🔍 Procesando solo variantes sin imagen")
        else:
            self.stdout.write(self.style.WARNING("⚠️ Modo FORCE: regenerando todas las imágenes"))
        
        # Obtener variantes
        variantes = ProductoVariante.objects.filter(query).select_related('producto')
        
        if options['limit']:
            variantes = variantes[:options['limit']]
            self.stdout.write(f"📊 Limitado a {options['limit']} variantes")
        
        total = variantes.count()
        self.stdout.write(f"\n📋 Total de variantes a procesar: {total}\n")
        
        if total == 0:
            self.stdout.write(self.style.WARNING("No hay variantes para procesar."))
            return
        
        # Contadores
        exitos = 0
        errores = 0
        desde_cache = 0
        
        for idx, variante in enumerate(variantes, 1):
            self.stdout.write(f"\n[{idx}/{total}] Procesando: {variante}")
            
            try:
                # Verificar que el producto tenga imagen base
                if not (variante.producto.imagen or variante.producto.imagen_url):
                    self.stdout.write(self.style.WARNING(
                        f"  ⚠️ Producto sin imagen base, saltando..."
                    ))
                    errores += 1
                    continue
                
                # Preparar color
                target_color = variante.color
                if not target_color:
                    self.stdout.write(self.style.WARNING("  ⚠️ Variante sin color definido, saltando..."))
                    errores += 1
                    continue
                
                if not target_color.startswith('#'):
                    # Mapa básico de colores
                    color_map = {
                        'negro': '#000000', 'blanco': '#FFFFFF', 'rojo': '#FF0000',
                        'azul': '#0000FF', 'verde': '#00FF00', 'amarillo': '#FFFF00',
                        'naranja': '#FF8000', 'rosa': '#FF69B4', 'morado': '#800080',
                        'gris': '#808080', 'beige': '#F5F5DC', 'cafe': '#8B4513',
                        'café': '#8B4513', 'marrón': '#8B4513', 'marron': '#8B4513',
                        'celeste': '#87CEEB', 'turquesa': '#40E0D0', 'violeta': '#8A2BE2'
                    }
                    target_color = color_map.get(target_color.lower(), '#FF0000')
                
                target_color = target_color.upper()
                
                # Verificar caché
                if not options['force']:
                    cache_existente = ImagenColorCache.objects.filter(
                        variante=variante,
                        color_hex=target_color
                    ).first()
                    
                    if cache_existente:
                        self.stdout.write(self.style.SUCCESS(f"  ✅ Usando imagen desde caché"))
                        variante.imagen_url = cache_existente.imagen_url
                        variante.imagen_generada_ia = True
                        variante.save(update_fields=['imagen_url', 'imagen_generada_ia'])
                        desde_cache += 1
                        continue
                
                # Cargar imagen del producto base
                pil_image = None
                try:
                    if variante.producto.imagen and getattr(variante.producto.imagen, 'path', None):
                        pil_image = Image.open(variante.producto.imagen.path).convert('RGB')
                    elif variante.producto.imagen_url:
                        if variante.producto.imagen_url.startswith('http'):
                            self.stdout.write(f"  📥 Descargando imagen desde URL...")
                            resp = requests.get(variante.producto.imagen_url, timeout=15)
                            resp.raise_for_status()
                            pil_image = Image.open(io.BytesIO(resp.content)).convert('RGB')
                        else:
                            # URL relativa - archivo estático
                            from django.conf import settings
                            relative_path = variante.producto.imagen_url.lstrip('/').replace('/', os.sep)
                            static_path = os.path.join(settings.BASE_DIR, relative_path)
                            if os.path.exists(static_path):
                                pil_image = Image.open(static_path).convert('RGB')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ Error cargando imagen: {e}"))
                    errores += 1
                    continue
                
                if not pil_image:
                    self.stdout.write(self.style.WARNING("  ⚠️ No se pudo cargar imagen base"))
                    errores += 1
                    continue
                
                # Detectar categoría
                categoria = _detectar_categoria_producto(variante.producto)
                self.stdout.write(f"  🏷️ Categoría detectada: {categoria}")
                
                # Procesar con SAM
                self.stdout.write(f"  🤖 Procesando con IA (color: {target_color})...")
                result_pil = process_image_recolor(pil_image, target_color, categoria=categoria)
                
                # Guardar a Supabase
                self.stdout.write(f"  ☁️ Subiendo a Supabase...")
                buf = io.BytesIO()
                result_pil.save(buf, format='PNG')
                buf.seek(0)
                
                filename = f'variantes/auto_{variante.producto.id}_{variante.id}_{target_color.replace("#", "")}.png'
                file_content = ContentFile(buf.getvalue(), name=filename)
                nueva_url = subir_a_supabase(file_content)
                
                if nueva_url and nueva_url != "/static/imagenes/zapatos.avif":
                    # Actualizar variante
                    variante.imagen_url = nueva_url
                    variante.imagen_generada_ia = True
                    variante.save(update_fields=['imagen_url', 'imagen_generada_ia'])
                    
                    # Guardar en caché
                    ImagenColorCache.objects.update_or_create(
                        variante=variante,
                        color_hex=target_color,
                        defaults={'imagen_url': nueva_url}
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f"  ✅ Imagen generada exitosamente"))
                    exitos += 1
                else:
                    self.stdout.write(self.style.ERROR(f"  ❌ Error subiendo a Supabase"))
                    errores += 1
                    
            except SamUnavailableError as e:
                self.stdout.write(self.style.ERROR(f"  ❌ SAM no disponible: {e}"))
                self.stdout.write(self.style.WARNING("\nDetén el proceso y configura SAM con:"))
                self.stdout.write("  .\setup_sam_recolor.ps1")
                return
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error: {e}"))
                import traceback
                self.stdout.write(traceback.format_exc())
                errores += 1
        
        # Resumen final
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"\n✅ RESUMEN:"))
        self.stdout.write(f"  • Total procesadas: {total}")
        self.stdout.write(self.style.SUCCESS(f"  • Exitosas: {exitos}"))
        if desde_cache > 0:
            self.stdout.write(self.style.SUCCESS(f"  • Desde caché: {desde_cache}"))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f"  • Con errores: {errores}"))
        self.stdout.write("\n" + "="*60)
