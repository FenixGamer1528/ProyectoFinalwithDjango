from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render,HttpResponse, redirect
from .forms import LoginForm, RegistroForm 
from carrito.models import Producto,Pedido, UsuarioPersonalizado



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
    return render(request, 'dashboard/dashboard.html')

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
    return render(request, 'dashboard/dashboard.html')

def admin_dashboard(request):
    total_usuarios = UsuarioPersonalizado.objects.count()
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()

    context = {
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'total_pedidos': total_pedidos,
    }
    return render(request, 'dashboard/dashboard.html', context)
def gestion_productos(request):
    productos = Producto.objects.all()
    return render(request, 'dashboard/gestion_productos.html', {'productos': productos})
def gestion_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'dashboard/gestion_pedidos.html', {'pedidos': pedidos})

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



#productos

