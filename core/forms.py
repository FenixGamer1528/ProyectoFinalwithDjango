from django import forms
from django.contrib.auth.forms import UserCreationForm
from carrito.models import UsuarioPersonalizado
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    usuario = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)

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

    class Meta:
        model = UsuarioPersonalizado
        fields = ['username', 'email', 'password1', 'password2']
    
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

