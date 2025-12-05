from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import io
from datetime import datetime, timedelta
from PIL import Image

from carrito.models import UsuarioPersonalizado, Producto, Pedido, Carrito, ProductoVariante, Inventario
from core.models import Reporte, Incidencia, SeguimientoReporte
from .forms import ProductoForm, ProductoVarianteForm, InventarioForm
from .utils import AnalizadorDatos, ExportadorReportes
from .sam_recolor import process_image_recolor, SamUnavailableError

User = get_user_model()

def admin_dashboard(request):
    from dashboard.models import ActividadReciente
    
    total_usuarios = UsuarioPersonalizado.objects.count()
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()

    ultimos_usuarios = UsuarioPersonalizado.objects.order_by('-date_joined')[:5]
    actividades_recientes = ActividadReciente.objects.select_related('usuario').order_by('-fecha')[:10]

    context = {
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'total_pedidos': total_pedidos,
        'ultimos_usuarios': ultimos_usuarios,
        'actividades_recientes': actividades_recientes,
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
                # Guardar producto base con stock general
                instance = form.save(commit=False)
                # Guardar el tipo_producto como campo adicional (puedes usarlo en variantes)
                tipo_producto = request.POST.get('tipo_producto', 'ropa')
                # Guardamos temporalmente en un campo o lo usamos en el contexto
                instance.save()
                messages.success(request, f'Producto creado con {instance.stock} unidades totales. Ahora distribuye el stock en variantes (tallas y colores) desde el botón "Variantes".')
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
            # Guardar solo campos base del producto
            form.save()
            messages.success(request, 'Producto actualizado. Gestiona tallas y colores desde "Variantes".')
            return redirect('gestion_productos')
    else:
        form = ProductoForm(instance=producto)
    context = {'form': form, 'producto': producto}
    return render(request, 'dashboard/editar_producto.html', context)


def gestion_pedidos(request):
    """Vista principal de gestión de pedidos con filtros y búsqueda"""
    pedidos = Pedido.objects.select_related('usuario', 'producto').all()
    
    # Filtro por búsqueda
    search = request.GET.get('search', '')
    if search:
        pedidos = pedidos.filter(
            Q(numero__icontains=search) |
            Q(usuario__username__icontains=search) |
            Q(usuario__email__icontains=search) |
            Q(usuario__first_name__icontains=search) |
            Q(usuario__last_name__icontains=search)
        )
    
    # Filtro por estado
    estado = request.GET.get('estado', '')
    if estado and estado != 'todos':
        pedidos = pedidos.filter(estado=estado)
    
    # Estadísticas
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_procesando = Pedido.objects.filter(estado='procesando').count()
    pedidos_completados = Pedido.objects.filter(estado='completado').count()
    
    context = {
        'pedidos': pedidos,
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_procesando': pedidos_procesando,
        'pedidos_completados': pedidos_completados,
        'search_query': search,
        'estado_filtro': estado,
    }
    return render(request, 'dashboard/gestion_pedidos.html', context)


@login_required
def gestion_reportes(request):
    """Vista principal de gestión de reportes"""
    # Filtros
    buscar = request.GET.get('buscar', '')
    estado = request.GET.get('estado', '')
    tipo = request.GET.get('tipo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Query base
    reportes = Reporte.objects.all()
    
    # Aplicar filtros
    if buscar:
        reportes = reportes.filter(
            Q(titulo__icontains=buscar) |
            Q(descripcion__icontains=buscar) |
            Q(categoria__icontains=buscar)
        )
    
    if estado:
        reportes = reportes.filter(estado=estado)
    
    if tipo:
        reportes = reportes.filter(tipo=tipo)
    
    if fecha_desde:
        reportes = reportes.filter(fecha_creacion__gte=fecha_desde)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
        reportes = reportes.filter(fecha_creacion__lte=fecha_hasta_dt)
    
    # Ordenar
    reportes = reportes.order_by('-fecha_creacion')
    
    # Estadísticas
    total_reportes = Reporte.objects.count()
    reportes_pendientes = Reporte.objects.filter(estado='pendiente').count()
    reportes_en_proceso = Reporte.objects.filter(estado='en_proceso').count()
    
    context = {
        'reportes': reportes,
        'total_reportes': total_reportes,
        'reportes_pendientes': reportes_pendientes,
        'reportes_en_proceso': reportes_en_proceso,
        'buscar': buscar,
        'estado_filtro': estado,
        'tipo_filtro': tipo,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'estados': Reporte.ESTADOS,
        'tipos': Reporte.TIPOS,
    }
    
    return render(request, 'dashboard/gestion_reportes.html', context)


@login_required
def crear_reporte(request):
    """Vista para crear un nuevo reporte"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        prioridad = request.POST.get('prioridad', 'media')
        asignado_a_id = request.POST.get('asignado_a')
        
        reporte = Reporte.objects.create(
            titulo=titulo,
            categoria=categoria,
            tipo=tipo,
            descripcion=descripcion,
            prioridad=prioridad,
            creado_por=request.user,
            asignado_a_id=asignado_a_id if asignado_a_id else None
        )
        
        # Registrar seguimiento
        SeguimientoReporte.objects.create(
            reporte=reporte,
            usuario=request.user,
            accion='Creación',
            comentario=f'Reporte creado: {titulo}'
        )
        
        messages.success(request, 'Reporte creado exitosamente')
        return redirect('gestion_reportes')
    
    # GET: mostrar formulario
    usuarios = User.objects.filter(is_active=True)
    context = {
        'tipos': Reporte.TIPOS,
        'prioridades': Reporte.PRIORIDADES,
        'usuarios': usuarios,
    }
    return render(request, 'dashboard/crear_reporte.html', context)


@login_required
def detalle_reporte(request, reporte_id):
    """Vista de detalle de un reporte"""
    reporte = get_object_or_404(Reporte, id=reporte_id)
    incidencias = reporte.incidencias.all()
    seguimientos = reporte.seguimientos.all()
    usuarios = User.objects.filter(is_active=True)
    
    context = {
        'reporte': reporte,
        'incidencias': incidencias,
        'seguimientos': seguimientos,
        'usuarios': usuarios,
        'estados': Reporte.ESTADOS,
        'prioridades': Reporte.PRIORIDADES,
    }
    
    return render(request, 'dashboard/detalle_reporte.html', context)


@login_required
@require_POST
def actualizar_estado_reporte(request, reporte_id):
    """Actualiza el estado de un reporte"""
    reporte = get_object_or_404(Reporte, id=reporte_id)
    
    estado_anterior = reporte.estado
    nuevo_estado = request.POST.get('estado')
    comentario = request.POST.get('comentario', '')
    
    reporte.estado = nuevo_estado
    
    # Si se completa, registrar fecha
    if nuevo_estado == 'completado' and not reporte.fecha_completado:
        reporte.fecha_completado = timezone.now()
    
    reporte.save()
    
    # Registrar seguimiento
    SeguimientoReporte.objects.create(
        reporte=reporte,
        usuario=request.user,
        accion='Cambio de estado',
        comentario=comentario,
        estado_anterior=estado_anterior,
        estado_nuevo=nuevo_estado
    )
    
    messages.success(request, f'Estado actualizado a {reporte.get_estado_display()}')
    return redirect('detalle_reporte', reporte_id=reporte_id)


@login_required
@require_POST
def asignar_responsable_reporte(request, reporte_id):
    """Asigna un responsable a un reporte"""
    reporte = get_object_or_404(Reporte, id=reporte_id)
    
    usuario_id = request.POST.get('usuario_id')
    comentario = request.POST.get('comentario', '')
    
    usuario_anterior = reporte.asignado_a
    nuevo_usuario = User.objects.get(id=usuario_id) if usuario_id else None
    
    reporte.asignado_a = nuevo_usuario
    reporte.save()
    
    # Registrar seguimiento
    SeguimientoReporte.objects.create(
        reporte=reporte,
        usuario=request.user,
        accion='Asignación de responsable',
        comentario=f'Asignado a: {nuevo_usuario.username if nuevo_usuario else "Nadie"}. {comentario}'
    )
    
    messages.success(request, 'Responsable asignado correctamente')
    return redirect('detalle_reporte', reporte_id=reporte_id)


@login_required
def crear_incidencia(request, reporte_id=None):
    """Crea una nueva incidencia"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        severidad = request.POST.get('severidad', 'media')
        producto_afectado = request.POST.get('producto_afectado', '')
        cantidad_afectada = request.POST.get('cantidad_afectada')
        
        incidencia = Incidencia.objects.create(
            titulo=titulo,
            tipo=tipo,
            descripcion=descripcion,
            severidad=severidad,
            producto_afectado=producto_afectado,
            cantidad_afectada=int(cantidad_afectada) if cantidad_afectada else None,
            reportado_por=request.user,
            reporte_id=reporte_id if reporte_id else None
        )
        
        messages.success(request, 'Incidencia registrada exitosamente')
        
        if reporte_id:
            return redirect('detalle_reporte', reporte_id=reporte_id)
        return redirect('gestion_reportes')
    
    context = {
        'tipos_incidencia': Incidencia.TIPOS_INCIDENCIA,
        'severidades': Incidencia.SEVERIDADES,
        'reporte_id': reporte_id,
    }
    return render(request, 'dashboard/crear_incidencia.html', context)


@login_required
def analizar_ventas(request):
    """Genera análisis de ventas"""
    mes = request.GET.get('mes', timezone.now().month)
    anio = request.GET.get('anio', timezone.now().year)
    
    analisis = AnalizadorDatos.analizar_ventas_mensuales(int(mes), int(anio))
    
    # Convertir DataFrames de Polars a listas para el template
    if analisis:
        analisis['ventas_por_estado_list'] = analisis['ventas_por_estado'].to_dicts()
        analisis['ventas_por_ciudad_list'] = analisis['ventas_por_ciudad'].head(10).to_dicts()
    
    context = {
        'analisis': analisis,
        'mes': mes,
        'anio': anio,
    }
    
    return render(request, 'dashboard/analizar_ventas.html', context)


@login_required
def exportar_reporte_ventas(request):
    """Exporta reporte de ventas a Excel usando Polars"""
    mes = request.GET.get('mes', timezone.now().month)
    anio = request.GET.get('anio', timezone.now().year)
    formato = request.GET.get('formato', 'excel')
    
    analisis = AnalizadorDatos.analizar_ventas_mensuales(int(mes), int(anio))
    
    if not analisis:
        messages.warning(request, 'No hay datos disponibles para el periodo seleccionado')
        return redirect('analizar_ventas')
    
    if formato == 'excel':
        buffer = ExportadorReportes.generar_reporte_ventas_excel(analisis)
        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=reporte_ventas_{mes}_{anio}.xlsx'
        return response
    
    elif formato == 'csv':
        buffer = ExportadorReportes.exportar_csv(analisis['dataframe'])
        response = HttpResponse(buffer.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=reporte_ventas_{mes}_{anio}.csv'
        return response


@login_required
def analizar_inventario(request):
    """Genera análisis de inventario"""
    analisis = AnalizadorDatos.analizar_inventario()
    
    # Convertir DataFrames de Polars a listas para el template
    if analisis:
        analisis['analisis_stock_list'] = analisis['analisis_stock'].to_dicts()
        analisis['productos_criticos_list'] = analisis['productos_criticos'].to_dicts()
    
    # Detectar problemas automáticamente
    problemas = AnalizadorDatos.detectar_problemas_inventario()
    
    context = {
        'analisis': analisis,
        'problemas': problemas,
    }
    
    return render(request, 'dashboard/analizar_inventario.html', context)


@login_required
def exportar_reporte_inventario(request):
    """Exporta reporte de inventario a Excel usando Polars"""
    formato = request.GET.get('formato', 'excel')
    
    analisis = AnalizadorDatos.analizar_inventario()
    
    if not analisis:
        messages.warning(request, 'No hay datos disponibles')
        return redirect('analizar_inventario')
    
    if formato == 'excel':
        buffer = ExportadorReportes.generar_reporte_inventario_excel(analisis)
        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=reporte_inventario.xlsx'
        return response
    
    elif formato == 'csv':
        buffer = ExportadorReportes.exportar_csv(analisis['dataframe'])
        response = HttpResponse(buffer.read(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=reporte_inventario.csv'
        return response


@login_required
def detectar_problemas_automatico(request):
    """Detecta y registra problemas automáticamente"""
    problemas_detectados = AnalizadorDatos.detectar_problemas_inventario()
    
    for problema in problemas_detectados:
        # Verificar si ya existe una incidencia similar reciente
        existe = Incidencia.objects.filter(
            titulo=problema['titulo'],
            resuelto=False,
            fecha_reporte__gte=timezone.now() - timedelta(days=7)
        ).exists()
        
        if not existe:
            Incidencia.objects.create(
                titulo=problema['titulo'],
                tipo=problema['tipo'],
                descripcion=problema['descripcion'],
                severidad=problema['severidad'],
                producto_afectado=problema['producto'],
                cantidad_afectada=problema['cantidad'],
                reportado_por=request.user
            )
    
    if problemas_detectados:
        messages.success(request, f'Se detectaron y registraron {len(problemas_detectados)} problemas')
    else:
        messages.info(request, 'No se detectaron problemas en el inventario')
    
    return redirect('analizar_inventario')


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
@login_required
def dashboardCliente(request):
    # 1. Buscar el carrito del usuario y sus items
    #    Usamos get_or_create para manejar usuarios que aún no tienen carrito
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items_del_carrito = carrito.items.all()

    # 2. Buscar el historial de pedidos del usuario
    #    Filtramos los pedidos que pertenecen al usuario logueado
    pedidos_del_usuario = Pedido.objects.filter(usuario=request.user).order_by('-fecha')

    # 3. Buscar los productos marcados como destacados
    productos_destacados = Producto.objects.filter(destacado=True)

    # 4. Preparar el contexto para enviar todo a la plantilla
    context = {
        'usuario': request.user,
        'items': items_del_carrito,
        'pedidos': pedidos_del_usuario,
        'productosDestacados': productos_destacados
    }

    # 5. Renderizar la plantilla con todos los datos
    return render(request, 'dashboard/cliente_dashboard.html', context)


# ==================== GESTIÓN DE VARIANTES ====================

@login_required
def gestionar_variantes(request, producto_id):
    """Vista para gestionar variantes de un producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    variantes = ProductoVariante.objects.filter(producto=producto).select_related('producto')
    
    # Calcular stock total asignado en variantes
    stock_asignado = sum(v.stock for v in variantes)
    stock_disponible = producto.stock - stock_asignado
    
    # Obtener tallas únicas (PRIMERO la talla base, luego las de variantes)
    tallas_disponibles = []
    if producto.talla:
        tallas_disponibles.append(producto.talla)
    
    # Agregar tallas de variantes que no sean la base
    for v in variantes:
        if v.talla and v.talla not in tallas_disponibles:
            tallas_disponibles.append(v.talla)
    
    # Obtener colores únicos (PRIMERO el color base, luego los de variantes)
    colores_disponibles = []
    if producto.colores:
        colores_disponibles.append(producto.colores)
    
    # Agregar colores de variantes que no sean el base
    for v in variantes:
        if v.color and v.color not in colores_disponibles:
            colores_disponibles.append(v.color)
    
    if request.method == 'POST':
        form = ProductoVarianteForm(request.POST, request.FILES)
        if form.is_valid():
            variante = form.save(commit=False)
            variante.producto = producto
            
            # Validar que el stock de la variante no exceda el disponible
            if variante.stock > stock_disponible:
                exceso = variante.stock - stock_disponible
                messages.error(
                    request, 
                    f'❌ ERROR: No hay suficiente stock. '
                    f'Intentas asignar {variante.stock} unidades pero solo hay {stock_disponible} disponibles. '
                    f'Te excedes por {exceso} unidad{"es" if exceso > 1 else ""}. '
                    f'(Stock total: {producto.stock} | Ya asignado: {stock_asignado})'
                )
                return redirect('gestionar_variantes', producto_id=producto.id)
            
            # Validar stock mínimo
            if variante.stock <= 0:
                messages.error(request, '❌ ERROR: El stock debe ser mayor a 0.')
                return redirect('gestionar_variantes', producto_id=producto.id)
            
            variante.save()
            
            # Crear registro inicial en inventario
            Inventario.objects.create(
                variante=variante,
                tipo_movimiento='entrada',
                cantidad=variante.stock,
                stock_anterior=0,
                stock_nuevo=variante.stock,
                usuario=request.user,
                observaciones='Stock inicial al crear variante'
            )
            
            # Recalcular stock disponible
            nuevo_stock_asignado = stock_asignado + variante.stock
            nuevo_stock_disponible = producto.stock - nuevo_stock_asignado
            porcentaje = int((nuevo_stock_asignado / producto.stock) * 100) if producto.stock > 0 else 0
            
            messages.success(
                request, 
                f'✅ Variante {variante.color} - {variante.talla} creada con {variante.stock} unidades. '
                f'Stock distribuido: {nuevo_stock_asignado}/{producto.stock} ({porcentaje}%) | '
                f'Stock disponible: {nuevo_stock_disponible} unidades.'
            )
            return redirect('gestionar_variantes', producto_id=producto.id)
    else:
        form = ProductoVarianteForm()
    
    context = {
        'producto': producto,
        'variantes': variantes,
        'tallas_disponibles': tallas_disponibles,
        'colores_disponibles': colores_disponibles,
        'form': form,
        'stock_total': producto.stock,
        'stock_asignado': stock_asignado,
        'stock_disponible': stock_disponible,
    }
    return render(request, 'dashboard/gestionar_variantes.html', context)


@login_required
def editar_variante(request, variante_id):
    """Editar una variante existente"""
    variante = get_object_or_404(ProductoVariante, id=variante_id)
    
    if request.method == 'POST':
        stock_anterior = variante.stock
        form = ProductoVarianteForm(request.POST, request.FILES, instance=variante)
        if form.is_valid():
            variante = form.save()
            
            # Si cambió el stock, registrar en inventario
            if variante.stock != stock_anterior:
                diferencia = variante.stock - stock_anterior
                tipo = 'entrada' if diferencia > 0 else 'salida'
                Inventario.objects.create(
                    variante=variante,
                    tipo_movimiento=tipo,
                    cantidad=abs(diferencia),
                    stock_anterior=stock_anterior,
                    stock_nuevo=variante.stock,
                    usuario=request.user,
                    observaciones='Ajuste manual de stock'
                )
            
            messages.success(request, 'Variante actualizada.')
            return redirect('gestionar_variantes', producto_id=variante.producto.id)
    else:
        form = ProductoVarianteForm(instance=variante)
    
    context = {'form': form, 'variante': variante}
    return render(request, 'dashboard/editar_variante.html', context)


@login_required
@require_POST
def eliminar_variante(request, variante_id):
    """Eliminar una variante"""
    variante = get_object_or_404(ProductoVariante, id=variante_id)
    producto_id = variante.producto.id
    variante.delete()
    messages.success(request, 'Variante eliminada.')
    return redirect('gestionar_variantes', producto_id=producto_id)


@login_required
def historial_inventario(request, variante_id):
    """Ver historial de movimientos de inventario de una variante"""
    variante = get_object_or_404(ProductoVariante, id=variante_id)
    movimientos = Inventario.objects.filter(variante=variante).select_related('usuario')
    
    context = {
        'variante': variante,
        'movimientos': movimientos,
    }
    return render(request, 'dashboard/historial_inventario.html', context)


@login_required
def ajustar_inventario(request, variante_id):
    """Registrar entrada/salida de inventario"""
    variante = get_object_or_404(ProductoVariante, id=variante_id)
    
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.variante = variante
            movimiento.stock_anterior = variante.stock
            movimiento.usuario = request.user
            
            # Calcular nuevo stock
            if movimiento.tipo_movimiento == 'entrada':
                movimiento.stock_nuevo = variante.stock + movimiento.cantidad
            elif movimiento.tipo_movimiento == 'salida':
                movimiento.stock_nuevo = max(0, variante.stock - movimiento.cantidad)
            else:  # ajuste
                movimiento.stock_nuevo = movimiento.cantidad
                movimiento.cantidad = abs(movimiento.stock_nuevo - variante.stock)
            
            movimiento.save()
            
            # Actualizar stock de la variante
            variante.stock = movimiento.stock_nuevo
            variante.save()
            
            messages.success(request, f'Inventario actualizado. Stock nuevo: {variante.stock}')
            return redirect('historial_inventario', variante_id=variante.id)
    else:
        form = InventarioForm()
    
    context = {
        'variante': variante,
        'form': form,
    }
    return render(request, 'dashboard/ajustar_inventario.html', context)


# ==================== API para cambio de color con IA ====================

def _detectar_categoria_producto(producto):
    """
    Detecta la categoría específica del producto para usar configuración optimizada.
    
    Mapea categorías de Django a categorías de configuración SAM:
    - 'zapatos' -> 'zapatos' (más saturación, brillo alto)
    - 'mujer', 'hombre' -> 'ropa' (configuración balanceada)
    - Accesorios detectados por nombre -> 'accesorios' (saturación máxima)
    - Bolsos detectados por nombre -> 'bolsos' (configuración intermedia)
    
    Returns:
        str: Categoría para configuración ('zapatos', 'ropa', 'accesorios', 'bolsos', 'general')
    """
    nombre_lower = producto.nombre.lower()
    descripcion_lower = producto.descripcion.lower() if producto.descripcion else ''
    
    # Mapeo directo de categoría Django
    if producto.categoria == 'zapatos':
        return 'zapatos'
    
    # Detectar accesorios por palabras clave
    keywords_accesorios = ['gafas', 'bufanda', 'cinturon', 'corbata', 'pañuelo', 'sombrero', 'gorra', 'reloj']
    if any(keyword in nombre_lower or keyword in descripcion_lower for keyword in keywords_accesorios):
        return 'accesorios'
    
    # Detectar bolsos
    keywords_bolsos = ['bolso', 'bolsa', 'cartera', 'mochila', 'morral']
    if any(keyword in nombre_lower or keyword in descripcion_lower for keyword in keywords_bolsos):
        return 'bolsos'
    
    # Categorías mujer/hombre son típicamente ropa
    if producto.categoria in ['mujer', 'hombre']:
        return 'ropa'
    
    # Por defecto: configuración general
    return 'general'


def generar_imagen_color(request, variante_id):
    """
    API endpoint para recolorizar imágenes usando Segment Anything (SAM) + recolor HSV.
    
    Modos de uso:
    1. POST con archivo 'image' + 'color' (hex): procesa imagen enviada
    2. POST/GET con solo 'color': usa imagen existente de la variante/producto
    
    Devuelve:
    - JSON con success, mensaje, imagen_url (subida a Supabase) e imagen_base64 (preview)
    """
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from core.utils.supabase_storage import subir_a_supabase
    import requests
    import base64
    
    variante = get_object_or_404(ProductoVariante, id=variante_id)
    
    # 1. Obtener imagen origen (POST upload o imagen existente)
    pil_image = None
    imagen_origen = None
    
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"DEBUG: variante.imagen_url = {variante.imagen_url}")
        logger.error(f"DEBUG: producto.imagen_url = {variante.producto.imagen_url if hasattr(variante.producto, 'imagen_url') else 'N/A'}")
        # Prioridad 1: imagen enviada en POST
        if request.FILES.get('image'):
            uploaded_file = request.FILES['image']
            pil_image = Image.open(uploaded_file).convert('RGB')
            imagen_origen = 'upload'
        # Prioridad 2: imagen de variante existente
        elif variante.imagen and getattr(variante.imagen, 'path', None):
            pil_image = Image.open(variante.imagen.path).convert('RGB')
            imagen_origen = 'variante_local'
        elif variante.imagen_url:
            # Verificar si es URL relativa (archivo estático) o URL completa
            if variante.imagen_url.startswith('http'):
                resp = requests.get(variante.imagen_url, timeout=10)
                resp.raise_for_status()
                pil_image = Image.open(io.BytesIO(resp.content)).convert('RGB')
                imagen_origen = 'variante_url'
            else:
                # URL relativa - construir ruta del archivo estático
                from django.conf import settings
                import os
                # Normalizar barras para Windows
                relative_path = variante.imagen_url.lstrip('/').replace('/', os.sep)
                static_path = os.path.join(settings.BASE_DIR, relative_path)
                if os.path.exists(static_path):
                    pil_image = Image.open(static_path).convert('RGB')
                    imagen_origen = 'variante_static'
                else:
                    raise FileNotFoundError(f'Archivo estático no encontrado: {static_path}')
        # Prioridad 3: imagen del producto base
        elif variante.producto.imagen and getattr(variante.producto.imagen, 'path', None):
            pil_image = Image.open(variante.producto.imagen.path).convert('RGB')
            imagen_origen = 'producto_local'
        elif variante.producto.imagen_url:
            # Verificar si es URL relativa o completa
            if variante.producto.imagen_url.startswith('http'):
                resp = requests.get(variante.producto.imagen_url, timeout=10)
                resp.raise_for_status()
                pil_image = Image.open(io.BytesIO(resp.content)).convert('RGB')
                imagen_origen = 'producto_url'
            else:
                # URL relativa - archivo estático
                from django.conf import settings
                import os
                # Normalizar barras para Windows
                relative_path = variante.producto.imagen_url.lstrip('/').replace('/', os.sep)
                static_path = os.path.join(settings.BASE_DIR, relative_path)
                if os.path.exists(static_path):
                    pil_image = Image.open(static_path).convert('RGB')
                    imagen_origen = 'producto_static'
                else:
                    raise FileNotFoundError(f'Archivo estático no encontrado: {static_path}')
        
        if pil_image is None:
            return JsonResponse({
                'success': False, 
                'mensaje': 'No se encontró imagen. Envíe una imagen en el campo "image" o asocie una imagen a la variante/producto.'
            }, status=400)
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"TRACEBACK COMPLETO: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'mensaje': f'Error al cargar imagen: {e}'}, status=500)
    
    # 2. Obtener color objetivo
    target_color = request.POST.get('color') or request.GET.get('color')
    if not target_color:
        target_color = f'#{variante.color}' if variante.color and not variante.color.startswith('#') else (variante.color or '#ff0000')
    
    # 3. Detectar categoría del producto para usar configuración optimizada
    categoria_producto = _detectar_categoria_producto(variante.producto)
    
    # 4. Procesar con SAM + recolor usando configuración específica
    try:
        result_pil = process_image_recolor(pil_image, target_color, categoria=categoria_producto)
    except SamUnavailableError as e:
        return JsonResponse({
            'success': False, 
            'mensaje': f'SAM no disponible: {e}. Verifica que hayas instalado segment-anything y definido SAM_CHECKPOINT.'
        }, status=500)
    except Exception as e:
        return JsonResponse({'success': False, 'mensaje': f'Error procesando imagen: {e}'}, status=500)
    
    # 5. Guardar resultado en memoria
    buf = io.BytesIO()
    result_pil.save(buf, format='PNG')
    buf.seek(0)
    
    # 6. Subir a Supabase
    nueva_url = None
    try:
        from django.core.files.base import ContentFile
        filename = f'variantes/recolor_{variante.producto.id}_{variante.id}_{target_color.replace("#", "")}.png'
        file_content = ContentFile(buf.getvalue(), name=filename)
        nueva_url = subir_a_supabase(file_content)
        
        if nueva_url and nueva_url != "/static/imagenes/zapatos.avif":  # Verificar que no sea URL de prueba
            # Actualizar variante con nueva imagen
            variante.imagen_url = nueva_url
            variante.imagen_generada_ia = True
            variante.save()
    except Exception as e:
        print(f'⚠️ Error subiendo a Supabase: {e}')
        # Continuar aunque falle Supabase - devolver base64
    
    # 6. Generar base64 para preview
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode('ascii')
    
    return JsonResponse({
        'success': True,
        'mensaje': f'Imagen recolorizada a {target_color} usando SAM (origen: {imagen_origen})',
        'imagen_url': nueva_url or variante.imagen_url,
        'imagen_generada_ia': True,
        'image_base64': f'data:image/png;base64,{encoded}',
        'variante_id': variante.id,
        'color_aplicado': target_color,
    })


# ==================== API para obtener variantes ====================

def obtener_variantes_producto(request, producto_id):
    """API endpoint para obtener variantes de un producto (usado en frontend)"""
    variantes = ProductoVariante.objects.filter(producto_id=producto_id).values(
        'id', 'talla', 'color', 'stock', 'imagen_url', 'tipo_producto', 'imagen_generada_ia'
    )
    return JsonResponse(list(variantes), safe=False)


def obtener_producto_detalle(request, producto_id):
    """API endpoint para obtener información completa de un producto"""
    try:
        producto = Producto.objects.get(id=producto_id)
        variantes = ProductoVariante.objects.filter(producto=producto).values(
            'id', 'talla', 'color', 'stock', 'imagen_url', 'tipo_producto', 'imagen_generada_ia'
        )
        
        data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'descripcion': producto.descripcion or 'Sin descripción',
            'categoria': producto.get_categoria_display(),
            'imagen_url': producto.imagen_url or (producto.imagen.url if producto.imagen else None),
            'stock': producto.stock,
            'destacado': producto.destacado,
            'variantes': list(variantes),
            'tallas_disponibles': list(set(v['talla'] for v in variantes)),
            'colores_disponibles': list(set(v['color'] for v in variantes))
        }
        
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


def obtener_inventario_completo(request):
    """API endpoint para obtener el inventario completo de todos los productos"""
    productos = Producto.objects.all().prefetch_related('variantes')
    
    inventario_data = []
    for producto in productos:
        variantes = producto.variantes.all()
        
        if variantes.exists():
            for variante in variantes:
                inventario_data.append({
                    'producto_id': producto.id,
                    'producto_nombre': producto.nombre,
                    'producto_imagen': producto.imagen_url or (producto.imagen.url if producto.imagen else None),
                    'variante_id': variante.id,
                    'talla': variante.talla,
                    'color': variante.color,
                    'stock': variante.stock,
                    'tipo_producto': variante.tipo_producto,
                    'precio': float(producto.precio)
                })
        else:
            # Producto sin variantes
            inventario_data.append({
                'producto_id': producto.id,
                'producto_nombre': producto.nombre,
                'producto_imagen': producto.imagen_url or (producto.imagen.url if producto.imagen else None),
                'variante_id': None,
                'talla': '-',
                'color': '-',
                'stock': producto.stock,
                'tipo_producto': None,
                'precio': float(producto.precio)
            })
    
    return JsonResponse(inventario_data, safe=False)


# ==================== GESTIÓN DE PEDIDOS ====================

@login_required
def detalle_pedido(request, pedido_id):
    """Vista para ver los detalles completos de un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    context = {
        'pedido': pedido,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si es una petición AJAX, devolver JSON
        data = {
            'numero': pedido.numero,
            'cliente': pedido.cliente,
            'email': pedido.email,
            'telefono': pedido.telefono or 'No especificado',
            'direccion': pedido.direccion or 'No especificada',
            'ciudad': pedido.ciudad or 'No especificada',
            'codigo_postal': pedido.codigo_postal or 'No especificado',
            'producto': {
                'nombre': pedido.producto.nombre,
                'imagen': pedido.producto.imagen_url or (pedido.producto.imagen.url if pedido.producto.imagen else None),
                'precio': str(pedido.producto.precio),
            },
            'cantidad': pedido.cantidad,
            'total': str(pedido.total),
            'estado': pedido.get_estado_display(),
            'estado_valor': pedido.estado,
            'notas': pedido.notas or 'Sin notas',
            'fecha': pedido.fecha.strftime('%d/%m/%Y %H:%M'),
            'fecha_actualizacion': pedido.fecha_actualizacion.strftime('%d/%m/%Y %H:%M'),
        }
        return JsonResponse(data)
    
    return render(request, 'dashboard/detalle_pedido.html', context)


@login_required
@require_POST
def actualizar_estado_pedido(request, pedido_id):
    """Vista para actualizar el estado de un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    nuevo_estado = request.POST.get('estado')
    
    if nuevo_estado in ['pendiente', 'procesando', 'completado', 'cancelado']:
        pedido.estado = nuevo_estado
        pedido.save()
        
        messages.success(request, f'Estado del pedido {pedido.numero} actualizado a {pedido.get_estado_display()}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'mensaje': f'Estado actualizado a {pedido.get_estado_display()}',
                'estado': pedido.estado,
                'estado_display': pedido.get_estado_display()
            })
    else:
        messages.error(request, 'Estado no válido')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'mensaje': 'Estado no válido'}, status=400)
    
    return redirect('gestion_pedidos')


@login_required
def eliminar_pedido(request, pedido_id):
    """Vista para eliminar un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    numero = pedido.numero
    
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, f'Pedido {numero} eliminado correctamente')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'mensaje': f'Pedido {numero} eliminado'})
        
        return redirect('gestion_pedidos')
    
    return redirect('gestion_pedidos')


@login_required
def actualizar_pedido(request, pedido_id):
    """Vista para actualizar información del pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        # Actualizar campos editables
        pedido.direccion = request.POST.get('direccion', pedido.direccion)
        pedido.telefono = request.POST.get('telefono', pedido.telefono)
        pedido.ciudad = request.POST.get('ciudad', pedido.ciudad)
        pedido.codigo_postal = request.POST.get('codigo_postal', pedido.codigo_postal)
        pedido.notas = request.POST.get('notas', pedido.notas)
        pedido.estado = request.POST.get('estado', pedido.estado)
        
        pedido.save()
        messages.success(request, f'Pedido {pedido.numero} actualizado correctamente')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'mensaje': 'Pedido actualizado'})
    
    return redirect('gestion_pedidos')
