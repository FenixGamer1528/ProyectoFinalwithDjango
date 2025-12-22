from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from .models import Producto, Carrito, ItemCarrito, Pedido
from decimal import Decimal


@login_required
def cliente_dashboard(request):
    from django.core.cache import cache
    from django.db.models import Sum
    
    # 1. Obtener los items del carrito del usuario con optimización
    carrito, _ = Carrito.objects.prefetch_related(
        'items__producto'
    ).get_or_create(usuario=request.user)
    items_carrito = carrito.items.select_related('producto').only(
        'id', 'cantidad', 'talla', 'color',
        'producto__id', 'producto__nombre', 'producto__precio', 'producto__imagen_url'
    )
    
    # Calcular total de items en carrito eficientemente
    total_items_carrito = items_carrito.aggregate(total=Sum('cantidad'))['total'] or 0

    # 2. Obtener SOLO los pedidos del usuario actual con optimización
    pedidos_usuario = Pedido.objects.filter(
        usuario=request.user
    ).select_related('producto').only(
        'id', 'fecha', 'estado', 'total', 'cantidad',
        'producto__id', 'producto__nombre', 'producto__imagen_url'
    ).order_by('-fecha')[:20]  # Limitar a últimos 20 pedidos
    
    # Total de pedidos del usuario
    total_pedidos = Pedido.objects.filter(usuario=request.user).count()

    # 3. Obtener productos destacados con caché
    cache_key = 'productos_destacados_dashboard'
    productos_destacados = cache.get(cache_key)
    if productos_destacados is None:
        productos_destacados = Producto.objects.filter(
            destacado=True
        ).only('id', 'nombre', 'precio', 'imagen_url')[:8]
        cache.set(cache_key, productos_destacados, 600)  # Cache 10 minutos

    # 4. Crear el contexto con toda la información
    context = {
        'usuario': request.user,
        'items': items_carrito,
        'total_items_carrito': total_items_carrito,
        'pedidos': pedidos_usuario,
        'total_pedidos': total_pedidos,
        'productosDestacados': productos_destacados,
    }
    
    # 5. Renderizar la plantilla correcta
    return render(request, 'dashboard/cliente_dashboard.html', context)
# Lista de productos
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})


# Vista clásica del carrito
@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.prefetch_related(
        'items__producto'
    ).get_or_create(usuario=request.user)
    
    # Optimizar carga de items
    carrito.items_optimizados = carrito.items.select_related('producto').only(
        'id', 'cantidad', 'talla', 'color',
        'producto__id', 'producto__nombre', 'producto__precio', 'producto__imagen_url'
    )
    
    return render(request, 'carrito.html', {'carrito': carrito})


# Agregar producto al carrito (funciona con POST normal y con AJAX)
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    # ⚠️ VALIDACIÓN: Verificar si el producto tiene variantes
    from .models import ProductoVariante
    tiene_variantes = ProductoVariante.objects.filter(producto=producto).exists()
    
    if tiene_variantes:
        # Si tiene variantes, DEBE usar agregar_al_carrito_variante
        mensaje = 'Este producto requiere seleccionar talla y color. Por favor, usa el modal de detalles.'
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "ok": False,
                "error": mensaje
            }, status=400)
        else:
            messages.warning(request, mensaje)
            return redirect('index')
    
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    cantidad = int(request.POST.get('cantidad', 1))
    # Permitimos que el usuario envíe una talla y color opcional al agregar al carrito
    talla = request.POST.get('talla')
    if talla:
        talla = talla.strip()
    else:
        talla = None
    
    color = request.POST.get('color')
    if color:
        color = color.strip()
    else:
        color = None

    # Buscamos el item teniendo en cuenta la talla y color seleccionados (pueden ser None)
    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito, 
        producto=producto, 
        talla=talla,
        color=color
    )
    if not creado:
        item.cantidad += cantidad
    else:
        item.cantidad = cantidad
    item.save()

    # ✅ Si es AJAX, responde con JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "ok": True,
            "item": {
                "id": item.id,
                "producto": producto.nombre,
                "cantidad": item.cantidad,
                "talla": item.talla,
                "color": item.color,
                "subtotal": float(item.subtotal())
            }
        })

    # ✅ Si no es AJAX, redirige normalmente
    messages.success(request, f'{producto.nombre} agregado al carrito')
    return redirect('index')


# Agregar variante específica al carrito (para productos con variantes de talla/color)
@login_required
@require_POST
def agregar_al_carrito_variante(request):
    """Agrega una variante específica (con talla y color) al carrito"""
    from .models import ProductoVariante
    
    variante_id = request.POST.get('variante_id')
    cantidad = int(request.POST.get('cantidad', 1))
    
    if not variante_id:
        return JsonResponse({
            'success': False,
            'error': 'Debes seleccionar una talla y color'
        }, status=400)
    
    # Obtener la variante
    variante = get_object_or_404(ProductoVariante, id=variante_id)
    producto = variante.producto
    
    # Verificar stock
    if variante.stock <= 0:
        return JsonResponse({
            'success': False,
            'error': 'Este producto no está disponible (sin stock)'
        }, status=400)
    
    if variante.stock < cantidad:
        return JsonResponse({
            'success': False,
            'error': f'Solo hay {variante.stock} unidades disponibles'
        }, status=400)
    
    # Obtener o crear el carrito
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    
    # Buscar si ya existe un item con esta variante exacta (talla + color)
    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        talla=variante.talla,
        color=variante.color,
        defaults={'cantidad': cantidad}
    )
    
    if not creado:
        # Si ya existe, incrementar cantidad
        nueva_cantidad = item.cantidad + cantidad
        if nueva_cantidad > variante.stock:
            return JsonResponse({
                'success': False,
                'error': f'Stock insuficiente. Solo hay {variante.stock} unidades disponibles'
            }, status=400)
        item.cantidad = nueva_cantidad
        item.save()
    
    # Responder con éxito
    return JsonResponse({
        'success': True,
        'message': f'Agregado al carrito: {producto.nombre} - {variante.color} - Talla {variante.talla}',
        'item': {
            'id': item.id,
            'producto': producto.nombre,
            'talla': variante.talla,
            'color': variante.color,
            'cantidad': item.cantidad,
            'precio': float(producto.precio),
            'subtotal': float(item.subtotal())
        },
        'carrito_total': carrito.items.count()
    })


# Eliminar producto del carrito
@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    if item.carrito.usuario == request.user:
        item.delete()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False}, status=403)


# Modal del carrito (JSON)
@login_required
def carrito_modal(request):
    carrito, _ = Carrito.objects.prefetch_related('items__producto').get_or_create(usuario=request.user)
    items = carrito.items.select_related('producto').all()

    datos = []
    for item in items:
        datos.append({
            'id': item.id,
            'producto': item.producto.nombre,
            'imagen': item.producto.imagen_url if item.producto.imagen_url else (item.producto.imagen.url if item.producto.imagen else ''),
            'precio': float(item.producto.precio),
            'cantidad': item.cantidad,
            'talla': item.talla or 'N/A',
            'color': item.color or 'N/A',
            'subtotal': float(item.subtotal())
        })
    
    return JsonResponse({'items': datos, 'total': float(carrito.total())})


# Página de detalle de un producto
def producto(request, product_id):
    producto = get_object_or_404(Producto, id=product_id)
    context = {'producto': producto}
    return render(request, 'producto.html', context)


@login_required
@require_POST
def toggle_favorito(request, producto_id):
    """Alterna el favorito (lista de deseos) del usuario para un producto.

    Responde JSON: {ok: True, added: True/False, total_favorites: int}
    """
    producto = get_object_or_404(Producto, id=producto_id)
    user = request.user
    # Asegurarse de que el usuario tenga el atributo favoritos (modelo personalizado)
    added = False
    if producto in user.favoritos.all():
        user.favoritos.remove(producto)
        added = False
    else:
        user.favoritos.add(producto)
        added = True

    total = user.favoritos.count()
    return JsonResponse({
        'ok': True,
        'added': added,
        'total_favorites': total,
        'producto_id': producto.id,
    })


@login_required
def mis_deseos(request):
    """Muestra la lista de deseos del usuario autenticado."""
    # Optimizado: usar only() para cargar solo campos necesarios
    productos = request.user.favoritos.only(
        'id', 'nombre', 'precio', 'imagen_url', 'destacado'
    ).all()
    context = {'productos': productos}
    return render(request, 'core/mis_deseos.html', context)


# Cambiar cantidad de un producto en el carrito
@login_required
@require_POST
def cambiar_cantidad(request, item_id, accion):
    try:
        item = get_object_or_404(ItemCarrito, id=item_id)
        
        # Validar que el item pertenece al usuario
        if item.carrito.usuario != request.user:
            return JsonResponse({"ok": False, "error": "No autorizado"}, status=403)
        
        print(f"🔄 Cambiando cantidad: item {item_id}, acción {accion}, cantidad actual: {item.cantidad}")
        
        if accion == "mas":
            item.cantidad += 1
            print(f"  ➕ Nueva cantidad: {item.cantidad}")
        elif accion == "menos" and item.cantidad > 1:
            item.cantidad -= 1
            print(f"  ➖ Nueva cantidad: {item.cantidad}")
        elif accion == "menos" and item.cantidad == 1:
            print(f"  ⚠️ No se puede reducir más (cantidad mínima: 1)")
            return JsonResponse({"ok": False, "error": "Cantidad mínima es 1"}, status=400)
        
        item.save()
        print(f"  ✅ Cantidad guardada: {item.cantidad}")
        
        # Calcular subtotal del item y total del carrito
        subtotal = float(item.subtotal())
        total_carrito = float(item.carrito.total())
        
        return JsonResponse({
            "ok": True, 
            "cantidad": item.cantidad,
            "subtotal": subtotal,
            "precio": float(item.producto.precio),
            "total_carrito": total_carrito
        })
    except Exception as e:
        print(f"  ❌ Error cambiando cantidad: {e}")
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
