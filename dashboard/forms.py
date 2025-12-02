from django import forms
from carrito.models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'stock', 'descripcion', 'imagen', 'destacado', 'en_oferta']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'categoria': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'precio': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'min': '0', 'placeholder': 'Stock total (ej: 80 unidades)'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
            'imagen': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'}),
            'en_oferta': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500'}),
        }