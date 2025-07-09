from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render,HttpResponse, redirect, get_object_or_404
from .forms import LoginForm, RegistroForm 
from .models import Producto,Pedido, UsuarioPersonalizado, Carrito, ItemCarrito
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

def home(request):
    productos = Producto.objects.all()
    return render(request, "core/home.html", {'productos': productos})


def about(request):
    return render(request, "about.html",{})

def index(request):
    productos= Producto.objects.all()
    print(productos)
    return render(request, 'index.html', {
        'productos': productos
  
})
  

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            password = form.cleaned_data['password']

            user = authenticate(request, username=usuario, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Redirige al home
            else:
                error_message = "Datos inválidos"
                return render(request, 'login.html', {'form': form, 'error_message': error_message})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            password = form.cleaned_data['password']
            user = authenticate(request, username=usuario, password=password)

            if user is not None:
                login(request, user)  # <- LOGIN SIEMPRE QUE SEA VÁLIDO
                
                if user.is_staff:
                    return redirect('dashboard')  # vista del admin
                else:
                    return redirect('index')   # vista del usuario normal
            else:
                error_message = "Datos inválidos"
                return render(request, 'login.html', {'form': form, 'error_message': error_message})
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def admin_dashboard(request):
    total_usuarios = UsuarioPersonalizado.objects.count()
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()

    context = {
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'total_pedidos': total_pedidos,
    }
    return render(request, 'core/dashboard.html', context)
def gestion_productos(request):
    productos = Producto.objects.all()
    return render(request, 'core/gestion_productos.html', {'productos': productos})
def gestion_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'core/gestion_pedidos.html', {'pedidos': pedidos})

#Registro de usuario

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('index')  # O a donde quieras redirigir
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})



#metodo home 



def portfolio(request):
    return HttpResponse(request,"core/portfolio.html")

def contact(request):
    return render(request, "core/contact.html")



# Carrito de compras.

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

#productos

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