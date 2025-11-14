from django import forms
from carrito.models import Producto, ProductoVariante, Inventario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'stock', 'talla', 'colores', 'descripcion', 'imagen', 'destacado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'categoria': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'precio': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'min': '0'}),
            'talla': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'placeholder': 'Ej: S, M, L, 38, 39'}),
            'colores': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'placeholder': 'Ej: Rojo, Azul, Negro'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
            'imagen': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
        }


class ProductoVarianteForm(forms.ModelForm):
    class Meta:
        model = ProductoVariante
        fields = ['tipo_producto', 'talla', 'color', 'stock', 'imagen']
        widgets = {
            'tipo_producto': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-black border border-[#C0A76B] rounded-md text-white'}),
            'talla': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-black border border-[#C0A76B] rounded-md text-white'}),
            'color': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-black border border-[#C0A76B] rounded-md text-white'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-black border border-[#C0A76B] rounded-md text-white', 'min': '0'}),
            'imagen': forms.FileInput(attrs={'class': 'w-full px-4 py-2 bg-black border border-[#C0A76B] rounded-md text-white'}),
        }


class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['tipo_movimiento', 'cantidad', 'observaciones']
        widgets = {
            'tipo_movimiento': forms.Select(attrs={'class': 'w-full px-4 py-2 bg-black border border-[#C0A76B] rounded-md text-white'}),
            'cantidad': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-black border border-[#C0A76B] rounded-md text-white', 'min': '1'}),
            'observaciones': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-black border border-[#C0A76B] rounded-md text-white', 'rows': 3}),
        }