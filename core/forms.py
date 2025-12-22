from django import forms
from django.contrib.auth.forms import UserCreationForm
from carrito.models import UsuarioPersonalizado
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    usuario = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    otp_code = forms.CharField(
        max_length=6, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Código 2FA (opcional)',
            'class': 'w-full px-4 py-3 bg-black/50 border border-[#C0A76B] rounded-lg text-white placeholder-gray-400'
        }),
        label='Código 2FA'
    )

class RegistroForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña', 
        widget=forms.PasswordInput,
        min_length=8,
        help_text='La contraseña debe tener al menos 8 caracteres.'
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña', 
        widget=forms.PasswordInput,
        help_text='Ingresa la misma contraseña para verificar.'
    )
    enable_2fa = forms.BooleanField(
        required=False,
        initial=False,
        label='Activar autenticación de dos factores (2FA)',
        help_text='Recomendado para mayor seguridad'
    )

    class Meta:
        model = UsuarioPersonalizado
        fields = ['username', 'email', 'password1', 'password2', 'enable_2fa']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UsuarioPersonalizado.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado. ¿Olvidaste tu contraseña?')
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class TwoFactorVerifyForm(forms.Form):
    """Formulario para verificar el código 2FA"""
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        label='Código de verificación',
        widget=forms.TextInput(attrs={
            'placeholder': '000000',
            'class': 'w-full px-4 py-3 bg-black/50 border border-[#C0A76B] rounded-lg text-white text-center text-2xl tracking-widest',
            'autocomplete': 'off',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}'
        }),
        help_text='Ingresa el código de 6 dígitos de tu app autenticadora'
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code')
        if not code.isdigit():
            raise ValidationError('El código debe contener solo números.')
        return code


class EditarPerfilForm(forms.ModelForm):
    """Formulario para editar información personal del usuario"""
    class Meta:
        model = UsuarioPersonalizado
        fields = ['first_name', 'last_name', 'email', 'telefono', 'direccion']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-black/50 border border-[#C0A76B] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-[#C0A76B] focus:ring-2 focus:ring-[#C0A76B]',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-black/50 border border-[#C0A76B] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-[#C0A76B] focus:ring-2 focus:ring-[#C0A76B]',
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-black/50 border border-[#C0A76B] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-[#C0A76B] focus:ring-2 focus:ring-[#C0A76B]',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-black/50 border border-[#C0A76B] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-[#C0A76B] focus:ring-2 focus:ring-[#C0A76B]',
                'placeholder': '3001234567'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-black/50 border border-[#C0A76B] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-[#C0A76B] focus:ring-2 focus:ring-[#C0A76B]',
                'placeholder': 'Calle 123 #45-67'
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }



