from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from carrito.models import UsuarioPersonalizado, Producto, Pedido, Carrito  # ProductoVariante, Inventario
from .forms import ProductoForm  # ProductoVarianteForm, InventarioForm

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

@login_required
def generar_imagen_color(request, variante_id):
    """
    Genera una nueva imagen del producto con el color seleccionado usando IA.
    Por ahora retorna la imagen original, pero aquí se integraría:
    - Replicate API (Stable Diffusion, ControlNet)
    - OpenAI DALL-E
    - Runway ML
    - etc.
    """
    variante = get_object_or_404(ProductoVariante, id=variante_id)
    
    # TODO: Integrar API de IA para cambio de color
    # Ejemplo conceptual:
    # imagen_original = variante.producto.imagen_url or variante.producto.imagen.url
    # prompt = f"Change the color of this {variante.producto.nombre} to {variante.color}, maintaining texture and lighting"
    # nueva_imagen_url = llamar_api_ia(imagen_original, prompt, variante.color)
    # variante.imagen_url = nueva_imagen_url
    # variante.imagen_generada_ia = True
    # variante.save()
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Funcionalidad de IA pendiente de integración',
        'imagen_url': variante.imagen_url or (variante.producto.imagen_url if variante.producto.imagen_url else None)
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
