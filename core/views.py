from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render,HttpResponse, redirect
from .forms import LoginForm 
from .models import Usuario,Producto


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

#Registro de usuario

# def registro_view(request):
#     if request.method == 'POST':
#         form = RegistroUsuarioForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Usuario creado exitosamente.')
#             return redirect('login')  # o donde desees redirigir
#     else:
#         form = RegistroUsuarioForm()
#     return render(request, 'registro.html', {'form': form})



#metodo home 



def portfolio(request):
    return HttpResponse(request,"core/portfolio.html")

def contact(request):
    return render(request, "core/contact.html")



# Create your views here.

