from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from .models import Producto, Carrito, ItemCarrito,Pedido
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


@login_required
def cliente_dashboard(request):
    # 1. Obtener los items del carrito del usuario con prefetch
    carrito, _ = Carrito.objects.prefetch_related(
        'items__producto'
    ).get_or_create(usuario=request.user)
    items_carrito = carrito.items.all()

    # 2. Obtener el historial de pedidos del usuario con select_related
    pedidos_usuario = Pedido.objects.filter(
        usuario=request.user
    ).select_related('producto').order_by('-fecha')[:10]  # Limitar a 10 últimos

    # 3. Obtener los productos destacados para mostrar
    productos_destacados = Producto.objects.filter(destacado=True).only(
        'id', 'nombre', 'precio', 'imagen_url'
    )[:6]  # Limitar a 6 productos

    # 4. Crear el contexto con toda la información
    context = {
        'usuario': request.user,
        'items': items_carrito,
        'pedidos': pedidos_usuario,
        'productosDestacados': productos_destacados,
    }
    
    # 5. Renderizar la plantilla con el contexto
    return render(request, 'cliente_dashboard.html', context)
# Lista de productos
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})


# Vista clásica del carrito
@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.prefetch_related('items__producto').get_or_create(usuario=request.user)
    return render(request, 'carrito.html', {'carrito': carrito})


# Agregar producto al carrito (funciona con POST normal y con AJAX)
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    cantidad = int(request.POST.get('cantidad', 1))
    # Permitimos que el usuario envíe una talla opcional al agregar al carrito
    talla = request.POST.get('talla')
    if talla:
        talla = talla.strip()
    else:
        talla = None

    # Buscamos el item teniendo en cuenta la talla seleccionada (puede ser None)
    item, creado = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto, talla=talla)
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
                "subtotal": float(item.subtotal())
            }
        })

    # ✅ Si no es AJAX, redirige normalmente
    return redirect('index')


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
            'talla': item.talla,
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
def cambiar_cantidad(request, item_id, accion):
    item = get_object_or_404(ItemCarrito, id=item_id)
    if accion == "mas":
        item.cantidad += 1
    elif accion == "menos" and item.cantidad > 1:
        item.cantidad -= 1
    item.save()
    return JsonResponse({"ok": True, "cantidad": item.cantidad})
