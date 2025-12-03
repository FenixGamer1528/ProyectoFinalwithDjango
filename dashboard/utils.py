"""
Utilidades para análisis de datos y generación de reportes con Polars
"""
import polars as pl
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from carrito.models import Pedido, Producto


class AnalizadorDatos:
    """Clase para análisis de datos del negocio"""
    
    @staticmethod
    def analizar_ventas_mensuales(mes=None, anio=None):
        """Analiza las ventas mensuales"""
        if not mes:
            mes = timezone.now().month
        if not anio:
            anio = timezone.now().year
            
        # Obtener pedidos del mes
        pedidos = Pedido.objects.filter(
            fecha__month=mes,
            fecha__year=anio,
            estado__in=['procesando', 'enviado', 'entregado']
        )
        
        # Convertir a DataFrame de Polars
        datos = []
        for pedido in pedidos:
            datos.append({
                'id_pedido': pedido.id,
                'fecha': pedido.fecha,
                'total': float(pedido.total),
                'estado': pedido.estado,
                'ciudad': pedido.ciudad or 'Sin especificar',
                'usuario': pedido.usuario.username if pedido.usuario else 'Invitado'
            })
        
        if not datos:
            return None
        
        df = pl.DataFrame(datos)
        
        # Análisis
        total_ventas = df['total'].sum()
        promedio_venta = df['total'].mean()
        cantidad_pedidos = len(df)
        
        # Ventas por estado
        ventas_por_estado = df.group_by('estado').agg([
            pl.col('total').sum().alias('total_ventas'),
            pl.col('id_pedido').count().alias('cantidad_pedidos')
        ])
        
        # Ventas por ciudad
        ventas_por_ciudad = df.group_by('ciudad').agg([
            pl.col('total').sum().alias('total_ventas'),
            pl.col('id_pedido').count().alias('cantidad_pedidos')
        ]).sort('total_ventas', descending=True)
        
        return {
            'dataframe': df,
            'total_ventas': total_ventas,
            'promedio_venta': promedio_venta,
            'cantidad_pedidos': cantidad_pedidos,
            'ventas_por_estado': ventas_por_estado,
            'ventas_por_ciudad': ventas_por_ciudad,
            'periodo': f"{mes}/{anio}"
        }
    
    @staticmethod
    def analizar_productos_vendidos(fecha_inicio=None, fecha_fin=None):
        """Analiza los productos más vendidos"""
        if not fecha_inicio:
            fecha_inicio = timezone.now() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = timezone.now()
        
        # Obtener pedidos
        pedidos = Pedido.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            estado__in=['procesando', 'enviado', 'entregado']
        ).select_related('producto')
        
        datos = []
        for pedido in pedidos:
            datos.append({
                'producto_id': pedido.producto.id,
                'producto_nombre': pedido.producto.nombre,
                'cantidad': pedido.cantidad,
                'precio': float(pedido.producto.precio),
                'subtotal': float(pedido.total),
                'fecha': pedido.fecha
            })
        
        if not datos:
            return None
        
        df = pl.DataFrame(datos)
        
        # Productos más vendidos
        productos_vendidos = df.group_by(['producto_id', 'producto_nombre']).agg([
            pl.col('cantidad').sum().alias('cantidad_vendida'),
            pl.col('subtotal').sum().alias('ingresos_generados'),
            pl.col('precio').mean().alias('precio_promedio')
        ]).sort('cantidad_vendida', descending=True)
        
        return {
            'dataframe': df,
            'productos_vendidos': productos_vendidos,
            'periodo': f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
        }
    
    @staticmethod
    def analizar_inventario():
        """Analiza el estado del inventario"""
        productos = Producto.objects.all()
        
        datos = []
        for producto in productos:
            # Determinar nivel de stock
            if producto.stock == 0:
                nivel_stock = 'Sin stock'
            elif producto.stock <= 5:
                nivel_stock = 'Stock bajo'
            elif producto.stock <= 20:
                nivel_stock = 'Stock medio'
            else:
                nivel_stock = 'Stock bueno'
            
            datos.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'stock': producto.stock,
                'precio': float(producto.precio),
                'nivel_stock': nivel_stock
            })
        
        if not datos:
            return None
        
        df = pl.DataFrame(datos)
        
        # Análisis por nivel de stock
        analisis_stock = df.group_by('nivel_stock').agg([
            pl.col('id').count().alias('cantidad_productos'),
            pl.col('stock').sum().alias('total_unidades')
        ])
        
        # Productos con stock crítico
        productos_criticos = df.filter(pl.col('stock') <= 5).sort('stock')
        
        # Valor del inventario
        df = df.with_columns((pl.col('stock') * pl.col('precio')).alias('valor_inventario'))
        valor_total = df['valor_inventario'].sum()
        
        return {
            'dataframe': df,
            'analisis_stock': analisis_stock,
            'productos_criticos': productos_criticos,
            'valor_total_inventario': valor_total,
            'total_productos': len(df)
        }
    
    @staticmethod
    def detectar_problemas_inventario():
        """Detecta problemas automáticamente en el inventario"""
        problemas = []
        
        # Productos sin stock
        sin_stock = Producto.objects.filter(stock=0)
        for producto in sin_stock:
            problemas.append({
                'tipo': 'stock',
                'severidad': 'alta',
                'titulo': f'Producto sin stock: {producto.nombre}',
                'descripcion': f'El producto {producto.nombre} (ID: {producto.id}) no tiene unidades disponibles.',
                'producto': producto.nombre,
                'cantidad': 0
            })
        
        # Productos con stock bajo
        stock_bajo = Producto.objects.filter(stock__lte=5, stock__gt=0)
        for producto in stock_bajo:
            problemas.append({
                'tipo': 'stock',
                'severidad': 'media',
                'titulo': f'Stock bajo: {producto.nombre}',
                'descripcion': f'El producto {producto.nombre} tiene solo {producto.stock} unidades disponibles.',
                'producto': producto.nombre,
                'cantidad': producto.stock
            })
        
        return problemas


class ExportadorReportes:
    """Clase para exportar reportes en diferentes formatos usando Polars"""
    
    @staticmethod
    def exportar_excel(df: pl.DataFrame, nombre_archivo: str, hoja: str = 'Datos'):
        """Exporta un DataFrame de Polars a Excel"""
        from io import BytesIO
        
        buffer = BytesIO()
        df.write_excel(buffer, worksheet=hoja)
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def exportar_csv(df: pl.DataFrame):
        """Exporta un DataFrame de Polars a CSV"""
        from io import BytesIO
        
        buffer = BytesIO()
        df.write_csv(buffer)
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def generar_reporte_ventas_excel(analisis_ventas):
        """Genera un reporte completo de ventas en Excel"""
        from io import BytesIO
        import xlsxwriter
        
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        
        # Formato para encabezados
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#C0A76B',
            'font_color': 'white',
            'border': 1
        })
        
        # Formato para números
        money_format = workbook.add_format({'num_format': '$#,##0.00'})
        
        # Hoja 1: Resumen
        worksheet_resumen = workbook.add_worksheet('Resumen')
        worksheet_resumen.write('A1', 'REPORTE DE VENTAS', header_format)
        worksheet_resumen.write('A2', 'Periodo:', header_format)
        worksheet_resumen.write('B2', analisis_ventas['periodo'])
        worksheet_resumen.write('A3', 'Total Ventas:', header_format)
        worksheet_resumen.write('B3', analisis_ventas['total_ventas'], money_format)
        worksheet_resumen.write('A4', 'Cantidad Pedidos:', header_format)
        worksheet_resumen.write('B4', analisis_ventas['cantidad_pedidos'])
        worksheet_resumen.write('A5', 'Promedio por Venta:', header_format)
        worksheet_resumen.write('B5', analisis_ventas['promedio_venta'], money_format)
        
        # Hoja 2: Detalle de pedidos
        worksheet_detalle = workbook.add_worksheet('Detalle Pedidos')
        df = analisis_ventas['dataframe']
        
        # Escribir encabezados
        for col_num, column in enumerate(df.columns):
            worksheet_detalle.write(0, col_num, column, header_format)
        
        # Escribir datos
        for row_num, row in enumerate(df.iter_rows()):
            for col_num, value in enumerate(row):
                if col_num == 2:  # Columna total
                    worksheet_detalle.write(row_num + 1, col_num, value, money_format)
                else:
                    worksheet_detalle.write(row_num + 1, col_num, str(value))
        
        # Hoja 3: Ventas por ciudad
        worksheet_ciudad = workbook.add_worksheet('Por Ciudad')
        df_ciudad = analisis_ventas['ventas_por_ciudad']
        
        for col_num, column in enumerate(df_ciudad.columns):
            worksheet_ciudad.write(0, col_num, column, header_format)
        
        for row_num, row in enumerate(df_ciudad.iter_rows()):
            for col_num, value in enumerate(row):
                if col_num == 1:  # Columna total_ventas
                    worksheet_ciudad.write(row_num + 1, col_num, value, money_format)
                else:
                    worksheet_ciudad.write(row_num + 1, col_num, str(value))
        
        workbook.close()
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def generar_reporte_inventario_excel(analisis_inventario):
        """Genera un reporte completo de inventario en Excel"""
        from io import BytesIO
        import xlsxwriter
        
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#C0A76B',
            'font_color': 'white',
            'border': 1
        })
        
        money_format = workbook.add_format({'num_format': '$#,##0.00'})
        
        # Hoja 1: Resumen
        worksheet_resumen = workbook.add_worksheet('Resumen')
        worksheet_resumen.write('A1', 'REPORTE DE INVENTARIO', header_format)
        worksheet_resumen.write('A2', 'Total Productos:', header_format)
        worksheet_resumen.write('B2', analisis_inventario['total_productos'])
        worksheet_resumen.write('A3', 'Valor Total Inventario:', header_format)
        worksheet_resumen.write('B3', analisis_inventario['valor_total_inventario'], money_format)
        
        # Hoja 2: Productos
        worksheet_productos = workbook.add_worksheet('Productos')
        df = analisis_inventario['dataframe']
        
        for col_num, column in enumerate(df.columns):
            worksheet_productos.write(0, col_num, column, header_format)
        
        for row_num, row in enumerate(df.iter_rows()):
            for col_num, value in enumerate(row):
                if col_num in [3, 6]:  # Columnas de precio y valor
                    worksheet_productos.write(row_num + 1, col_num, value, money_format)
                else:
                    worksheet_productos.write(row_num + 1, col_num, str(value))
        
        # Hoja 3: Productos críticos
        if len(analisis_inventario['productos_criticos']) > 0:
            worksheet_criticos = workbook.add_worksheet('Stock Crítico')
            df_criticos = analisis_inventario['productos_criticos']
            
            for col_num, column in enumerate(df_criticos.columns):
                worksheet_criticos.write(0, col_num, column, header_format)
            
            for row_num, row in enumerate(df_criticos.iter_rows()):
                for col_num, value in enumerate(row):
                    worksheet_criticos.write(row_num + 1, col_num, str(value))
        
        workbook.close()
        buffer.seek(0)
        
        return buffer
