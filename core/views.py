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