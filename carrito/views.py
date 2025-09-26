from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from .models import Producto, Carrito, ItemCarrito
from decimal import Decimal



# Lista de productos
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})


# Vista clásica del carrito
@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    return render(request, 'carrito.html', {'carrito': carrito})


# Agregar producto al carrito (funciona con POST normal y con AJAX)
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    cantidad = int(request.POST.get('cantidad', 1))

    item, creado = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
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
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()

    datos = []
    for item in items:
        # Convertir precio
        precio = item.producto.precio
        if isinstance(precio, Decimal):
            precio = precio.to_decimal()

        # Convertir subtotal
        subtotal = item.subtotal()
        if isinstance(subtotal, Decimal):
            subtotal = subtotal.to_decimal()

        datos.append({
            'id': item.id,
            'producto': item.producto.nombre,
            'imagen': item.producto.imagen.url if item.producto.imagen else '',
            'precio': float(precio),
            'cantidad': item.cantidad,
            'subtotal': float(subtotal)
        })

    total = carrito.total()
    if isinstance(total, Decimal):
        total = total.to_decimal()

    return JsonResponse({'items': datos, 'total': float(total)})


# Página de detalle de un producto
def producto(request, product_id):
    producto = get_object_or_404(Producto, id=product_id)
    context = {'producto': producto}
    return render(request, 'producto.html', context)


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
