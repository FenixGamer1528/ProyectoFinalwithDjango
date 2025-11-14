from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render,HttpResponse, redirect
from .forms import LoginForm, RegistroForm 
from carrito.models import Producto,Pedido, UsuarioPersonalizado
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q



def home(request):
    productos = Producto.objects.all()
    return render(request, "core/home.html", {'productos': productos})


def about(request):
    return render(request, "about.html",{})

def index(request):
    # Cargar productos destacados (para "Lo Más Vendido")
    productos = Producto.objects.filter(destacado=True).only(
        'id', 'nombre', 'precio', 'imagen_url', 'destacado', 'categoria'
    )
    
    # Cargar productos en oferta (para "Ofertas Especiales")
    productos_ofertas = Producto.objects.filter(en_oferta=True).only(
        'id', 'nombre', 'precio', 'imagen_url', 'en_oferta'
    )
    
    # Prefetch favoritos si el usuario está autenticado
    if request.user.is_authenticated:
        productos = productos.prefetch_related('favorited_by')
        productos_ofertas = productos_ofertas.prefetch_related('favorited_by')
    
    return render(request, 'index.html', {
        'productos': productos,
        'productos_ofertas': productos_ofertas
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
                login(request, user)  # Iniciar sesión
                
                # TODOS los usuarios van al index
                return redirect('index')
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
        
    }
    return render(request, 'dashboard/dashboard.html', context)
def gestion_productos(request):
    productos = Producto.objects.all()
    return render(request, 'dashboard/gestion_productos.html', {'productos': productos})

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

def buscar_productos(request):
    query = request.GET.get('q', '').strip()
    productos = []

    if query:
        # Búsqueda más precisa por nombre
        productos = Producto.objects.filter(nombre__iexact=query)
        
        # Si no encuentra resultados exactos, busca coincidencias parciales
        if not productos:
            productos = Producto.objects.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(categoria__icontains=query)
            )

    context = {
        'productos': productos,
        'query': query,
    }
    
    return render(request, 'core/resultados_busqueda.html', context)




from django.views.generic import ListView
from .models import Reporte
import openpyxl
from reportlab.pdfgen import canvas
from django.utils.timezone import localtime
from django.db.models import Q

class ReporteListView(ListView):
    model = Reporte
    template_name = 'reportes/lista_reportes.html'
    context_object_name = 'reportes'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '')
        estado = self.request.GET.get('estado', '')
        fecha_desde = self.request.GET.get('fecha_desde', '')
        fecha_hasta = self.request.GET.get('fecha_hasta', '')

        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) | Q(categoria__icontains=q)
            )
        if estado:
            queryset = queryset.filter(estado=estado)
        if fecha_desde:
            queryset = queryset.filter(fecha_creacion__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_creacion__date__lte=fecha_hasta)

        return queryset.order_by('-fecha_creacion')

def exportar_excel(request):
    reportes = Reporte.objects.all().order_by('-fecha_creacion')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reportes"

    headers = ['ID', 'Título', 'Categoría', 'Fecha de Creación', 'Estado']
    ws.append(headers)

    for r in reportes:
        ws.append([
            r.id,
            r.titulo,
            r.categoria,
            localtime(r.fecha_creacion).strftime('%d/%m/%Y %H:%M'),
            r.get_estado_display()
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=reportes.xlsx'
    wb.save(response)
    return response

def exportar_pdf(request):
    reportes = Reporte.objects.all().order_by('-fecha_creacion')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=reportes.pdf'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, 800, "Reporte de Reportes")

    y = 760
    p.setFont("Helvetica", 10)

    for r in reportes:
        texto = f"ID: {r.id} | Título: {r.titulo} | Categoría: {r.categoria} | Fecha: {localtime(r.fecha_creacion).strftime('%d/%m/%Y %H:%M')} | Estado: {r.get_estado_display()}"
        p.drawString(30, y, texto)
        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response

def hombres(request):
    # Optimizado: solo cargar campos necesarios y usar caché
    productos = Producto.objects.filter(categoria=Producto.CategoriaEnum.HOMBRE).only(
        'id', 'nombre', 'precio', 'imagen_url', 'destacado'
    )
    
    # Prefetch favoritos si el usuario está autenticado
    if request.user.is_authenticated:
        productos = productos.prefetch_related('favorited_by')
    
    return render(request, "core/hombres.html", {"productos": productos})


def mujeres(request):
    productos = Producto.objects.filter(categoria=Producto.CategoriaEnum.MUJER).only(
        'id', 'nombre', 'precio', 'imagen_url', 'destacado'
    )
    
    if request.user.is_authenticated:
        productos = productos.prefetch_related('favorited_by')
    
    return render(request, "core/mujeres.html", {"productos": productos})


def zapatos(request):
    productos = Producto.objects.filter(categoria=Producto.CategoriaEnum.ZAPATOS).only(
        'id', 'nombre', 'precio', 'imagen_url', 'destacado'
    )
    
    if request.user.is_authenticated:
        productos = productos.prefetch_related('favorited_by')
    
    return render(request, "core/zapatos.html", {"productos": productos})


def ofertas(request):
    # Mostrar productos marcados como "en_oferta"
    productos = Producto.objects.filter(en_oferta=True).only(
        'id', 'nombre', 'precio', 'imagen_url', 'en_oferta', 'descripcion'
    )
    
    # Prefetch favoritos si el usuario está autenticado
    if request.user.is_authenticated:
        productos = productos.prefetch_related('favorited_by')
    
    return render(request, "core/ofertas.html", {"productos": productos})


@login_required
def toggle_favorito(request, producto_id):
    # Aceptar tanto POST como GET para depuración
    if request.method not in ['POST', 'GET']:
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)
    
    try:
        print(f"Usuario: {request.user}, Producto ID: {producto_id}")  # Debug
        
        producto = get_object_or_404(Producto, id=producto_id)
        usuario = request.user
        
        # Verificar si el producto ya está en favoritos
        if producto in usuario.favoritos.all():
            usuario.favoritos.remove(producto)
            is_favorito = False
            mensaje = 'Producto eliminado de favoritos'
            print(f"Producto {producto_id} eliminado de favoritos")  # Debug
        else:
            usuario.favoritos.add(producto)
            is_favorito = True
            mensaje = 'Producto agregado a favoritos'
            print(f"Producto {producto_id} agregado a favoritos")  # Debug
        
        # Contar favoritos actualizados
        total_favoritos = usuario.favoritos.count()
        print(f"Total favoritos: {total_favoritos}")  # Debug
        
        return JsonResponse({
            'success': True,
            'is_favorito': is_favorito,
            'mensaje': mensaje,
            'total_favoritos': total_favoritos
        })
    except Exception as e:
        print(f"Error en toggle_favorito: {str(e)}")  # Debug
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def mis_deseos(request):
    productos = request.user.favoritos.all()
    return render(request, 'core/mis_deseos.html', {'productos': productos})


def producto_detalle(request, producto_id):
    """Vista de detalle del producto - simplificada sin variantes"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Verificar si es favorito
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = producto in request.user.favoritos.all()
    
    context = {
        'producto': producto,
        'es_favorito': es_favorito,
    }
    
    # Vista completa normal
    return render(request, 'core/producto.html', context)

