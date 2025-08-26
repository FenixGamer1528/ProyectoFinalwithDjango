from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Producto, Carrito, ItemCarrito
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models


# Create your views here.

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})

@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    return render(request, 'carrito.html', {'carrito': carrito})

@login_required
def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

        cantidad = int(request.POST.get('cantidad', 1))

        item, creado = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
        if not creado:
            item.cantidad += cantidad
        else:
            item.cantidad = cantidad
        item.save()

        return redirect('index')  # o donde quieras ir luego de agregar
    else:
        # Si alguien entra por GET, redirige o lanza un error
        return redirect('index')

@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id)
    if item.carrito.usuario == request.user:
        item.delete()
    return redirect('ver_carrito')

@login_required
def carrito_modal(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    datos = [{
        'id': item.id,
        'producto': item.producto.nombre,
        'precio': float(item.producto.precio),
        'cantidad': item.cantidad,
        'subtotal': float(item.subtotal())
    } for item in items]
    total = float(carrito.total())
    return JsonResponse({'items': datos, 'total': total})

def producto(request, product_id):
    producto = get_object_or_404(Producto, id=product_id)
    context = {'producto': producto}
    return render(request, 'producto.html', context)

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        # Logic to add product to cart (e.g., session-based or database-based cart)
        messages.success(request, 'Producto añadido al carrito')
        return redirect('index')
    return redirect('index')

def cambiar_cantidad(request, item_id, accion):
    item = get_object_or_404(CarritoItem, id=item_id)
    if accion == "mas":
        item.cantidad += 1
    elif accion == "menos" and item.cantidad > 1:
        item.cantidad -= 1
    item.save()
    return JsonResponse({"ok": True})

class CarritoItem(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad