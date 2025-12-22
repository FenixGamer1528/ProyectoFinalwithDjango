from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from carrito.models import Pedido, Producto, ProductoVariante
from core.models import Reporte, Incidencia
from dashboard.models import ActividadReciente

User = get_user_model()


@receiver(post_save, sender=User)
def registrar_actividad_usuario(sender, instance, created, **kwargs):
    """Registra cuando se crea un nuevo usuario"""
    if created:
        ActividadReciente.objects.create(
            tipo='registro',
            titulo='Nuevo usuario registrado',
            descripcion=f'{instance.username} se ha registrado en el sistema',
            usuario=instance,
            objeto_id=instance.id,
            objeto_tipo='Usuario'
        )


@receiver(post_save, sender=Pedido)
def registrar_actividad_pedido(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un pedido"""
    if created:
        ActividadReciente.objects.create(
            tipo='venta',
            titulo='Nuevo pedido realizado',
            descripcion=f'Pedido #{instance.id} - Total: ${instance.total}',
            usuario=instance.usuario if instance.usuario else None,
            objeto_id=instance.id,
            objeto_tipo='Pedido'
        )


@receiver(post_save, sender=Producto)
def registrar_actividad_producto(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un producto"""
    if created:
        ActividadReciente.objects.create(
            tipo='producto',
            titulo='Nuevo producto agregado',
            descripcion=f'{instance.nombre} ha sido agregado al inventario',
            usuario=None,
            objeto_id=instance.id,
            objeto_tipo='Producto'
        )
    else:
        # Verificar si el stock es bajo
        if hasattr(instance, 'stock') and instance.stock <= 10:
            ActividadReciente.objects.create(
                tipo='alerta',
                titulo='Alerta de stock bajo',
                descripcion=f'{instance.nombre} tiene solo {instance.stock} unidades disponibles',
                usuario=None,
                objeto_id=instance.id,
                objeto_tipo='Producto'
            )


@receiver(post_delete, sender=Producto)
def registrar_eliminacion_producto(sender, instance, **kwargs):
    """Registra cuando se elimina un producto"""
    ActividadReciente.objects.create(
        tipo='producto',
        titulo='Producto eliminado',
        descripcion=f'{instance.nombre} ha sido eliminado del sistema',
        usuario=None,
        objeto_id=instance.id,
        objeto_tipo='Producto'
    )


@receiver(post_save, sender=Reporte)
def registrar_actividad_reporte(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un reporte"""
    if created:
        ActividadReciente.objects.create(
            tipo='reporte',
            titulo='Nuevo reporte creado',
            descripcion=f'{instance.get_tipo_display()}: {instance.titulo}',
            usuario=instance.usuario,
            objeto_id=instance.id,
            objeto_tipo='Reporte'
        )
    elif instance.estado == 'resuelto':
        ActividadReciente.objects.create(
            tipo='reporte',
            titulo='Reporte resuelto',
            descripcion=f'{instance.titulo} ha sido marcado como resuelto',
            usuario=instance.responsable if instance.responsable else instance.usuario,
            objeto_id=instance.id,
            objeto_tipo='Reporte'
        )


@receiver(post_save, sender=Incidencia)
def registrar_actividad_incidencia(sender, instance, created, **kwargs):
    """Registra cuando se crea una incidencia"""
    if created:
        ActividadReciente.objects.create(
            tipo='incidencia',
            titulo='Nueva incidencia reportada',
            descripcion=f'{instance.get_tipo_display()}: {instance.descripcion[:50]}...',
            usuario=instance.reporte.usuario,
            objeto_id=instance.id,
            objeto_tipo='Incidencia'
        )


@receiver(post_save, sender=ProductoVariante)
def generar_imagen_ia_automatica(sender, instance, created, **kwargs):
    """
    Genera automáticamente imagen con IA cuando se crea una variante sin imagen propia.
    - Si la variante tiene imagen propia, no hace nada
    - Si no tiene imagen pero el color es diferente al producto base, genera con IA
    - Usa threading para no bloquear la creación de la variante
    """
    import threading
    
    # Solo procesar si:
    # 1. Es una nueva variante (created=True)
    # 2. No tiene imagen propia asignada
    # 3. No ha sido generada por IA anteriormente
    # 4. Tiene un color definido
    if not created or instance.imagen or instance.imagen_url or instance.imagen_generada_ia:
        return
    
    if not instance.color:
        return
    
    # Verificar que el producto tenga imagen base
    if not (instance.producto.imagen or instance.producto.imagen_url):
        print(f"⚠️ Producto {instance.producto.nombre} sin imagen base, no se puede generar variante con IA")
        return
    
    def generar_imagen_background():
        """Función que se ejecuta en background para generar la imagen"""
        try:
            from dashboard.sam_recolor import process_image_recolor, SamUnavailableError
            from PIL import Image
            from core.utils.supabase_storage import subir_a_supabase
            from dashboard.models import ImagenColorCache
            from django.core.files.base import ContentFile
            import io
            import requests
            
            print(f"🎨 Generando imagen con IA para variante: {instance}")
            
            # 1. Cargar imagen del producto base
            pil_image = None
            try:
                if instance.producto.imagen and getattr(instance.producto.imagen, 'path', None):
                    pil_image = Image.open(instance.producto.imagen.path).convert('RGB')
                elif instance.producto.imagen_url:
                    if instance.producto.imagen_url.startswith('http'):
                        resp = requests.get(instance.producto.imagen_url, timeout=15)
                        resp.raise_for_status()
                        pil_image = Image.open(io.BytesIO(resp.content)).convert('RGB')
                    else:
                        # URL relativa - archivo estático
                        from django.conf import settings
                        import os
                        relative_path = instance.producto.imagen_url.lstrip('/').replace('/', os.sep)
                        static_path = os.path.join(settings.BASE_DIR, relative_path)
                        if os.path.exists(static_path):
                            pil_image = Image.open(static_path).convert('RGB')
            except Exception as e:
                print(f"❌ Error cargando imagen base: {e}")
                return
            
            if not pil_image:
                print(f"⚠️ No se pudo cargar imagen base para {instance.producto.nombre}")
                return
            
            # 2. Preparar color objetivo
            target_color = instance.color
            if not target_color.startswith('#'):
                # Convertir nombre de color a hex (básico)
                color_map = {
                    'negro': '#000000', 'blanco': '#FFFFFF', 'rojo': '#FF0000',
                    'azul': '#0000FF', 'verde': '#00FF00', 'amarillo': '#FFFF00',
                    'naranja': '#FF8000', 'rosa': '#FF69B4', 'morado': '#800080',
                    'gris': '#808080', 'beige': '#F5F5DC', 'cafe': '#8B4513',
                    'café': '#8B4513', 'marrón': '#8B4513', 'marron': '#8B4513'
                }
                target_color = color_map.get(target_color.lower(), '#FF0000')
            
            target_color = target_color.upper()
            
            # 3. Verificar caché primero
            cache_existente = ImagenColorCache.objects.filter(
                variante=instance, 
                color_hex=target_color
            ).first()
            
            if cache_existente:
                print(f"✅ Usando imagen desde caché para {instance}")
                instance.imagen_url = cache_existente.imagen_url
                instance.imagen_generada_ia = True
                instance.save(update_fields=['imagen_url', 'imagen_generada_ia'])
                return
            
            # 4. Detectar categoría del producto
            from dashboard.views import _detectar_categoria_producto
            categoria = _detectar_categoria_producto(instance.producto)
            
            # 5. Procesar con SAM + recolor
            result_pil = process_image_recolor(pil_image, target_color, categoria=categoria)
            
            # 6. Guardar a Supabase
            buf = io.BytesIO()
            result_pil.save(buf, format='PNG')
            buf.seek(0)
            
            filename = f'variantes/auto_{instance.producto.id}_{instance.id}_{target_color.replace("#", "")}.png'
            file_content = ContentFile(buf.getvalue(), name=filename)
            nueva_url = subir_a_supabase(file_content)
            
            if nueva_url and nueva_url != "/static/imagenes/zapatos.avif":
                # Actualizar variante
                instance.imagen_url = nueva_url
                instance.imagen_generada_ia = True
                instance.save(update_fields=['imagen_url', 'imagen_generada_ia'])
                
                # Guardar en caché
                ImagenColorCache.objects.update_or_create(
                    variante=instance,
                    color_hex=target_color,
                    defaults={'imagen_url': nueva_url}
                )
                
                print(f"✅ Imagen generada automáticamente para {instance}")
            else:
                print(f"⚠️ No se pudo subir imagen a Supabase para {instance}")
                
        except SamUnavailableError as e:
            print(f"⚠️ SAM no disponible: {e}")
        except Exception as e:
            import traceback
            print(f"❌ Error generando imagen automática: {e}")
            print(traceback.format_exc())
    
    # Ejecutar en thread separado para no bloquear
    thread = threading.Thread(target=generar_imagen_background, daemon=True)
    thread.start()
