from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q

from carrito.models import UsuarioPersonalizado, Producto, Pedido
from .forms import ProductoForm

User = get_user_model()

def admin_dashboard(request):
    total_usuarios = UsuarioPersonalizado.objects.count()
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()

    ultimos_usuarios = UsuarioPersonalizado.objects.order_by('-date_joined')[:5]

    context = {
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'total_pedidos': total_pedidos,
        'ultimos_usuarios': ultimos_usuarios,
    }
    return render(request, 'dashboard/dashboard.html', context)


def gestion_usuarios(request):
    usuarios = UsuarioPersonalizado.objects.all()
    return render(request, 'dashboard/gestion_usuarios.html', {'usuarios': usuarios})


def eliminar_usuario(request, user_id):
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        usuario.delete()
        return redirect('gestion_usuarios')


def gestion_productos(request):
    productos = Producto.objects.all()
    search = request.GET.get('search', '')
    categoria = request.GET.get('categoria', 'all')
    
    if search:
        productos = productos.filter(
            Q(nombre__icontains=search) | Q(descripcion__icontains=search)
        )
    if categoria != 'all':
        productos = productos.filter(categoria=categoria)
    
    form = ProductoForm()
    if request.method == 'POST':
        if 'guardar' in request.POST:
            form = ProductoForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Producto guardado exitosamente.')
                return redirect('gestion_productos')
        elif 'eliminar' in request.POST:
            producto_id = request.POST.get('producto_id')
            producto = get_object_or_404(Producto, id=producto_id)
            producto.delete()
            messages.success(request, 'Producto eliminado.')
            return redirect('gestion_productos')
    
    context = {
        'productos': productos,
        'form': form,
        'search_query': search,
        'selected_categoria': categoria,
    }
    return render(request, 'dashboard/gestion_productos.html', context)


@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('gestion_productos')
    else:
        form = ProductoForm(instance=producto)
    context = {'form': form, 'producto': producto}
    return render(request, 'dashboard/editar_producto.html', context)


def gestion_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'dashboard/gestion_pedidos.html', {'pedidos': pedidos})


def gestion_reportes(request):
    return render(request, 'dashboard/gestion_reportes.html')


def configuracion(request):
    return render(request, 'dashboard/configuracion.html')


def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role') 
        is_active = request.POST.get('status') == 'on'
        password = User.objects.make_random_password()  

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active
        )
        return redirect('gestion_usuarios') 
    
    return render(request, 'dashboard/crear_usuario.html')
