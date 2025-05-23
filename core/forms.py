from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioPersonalizado

class LoginForm(forms.Form):
    usuario = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)

class RegistroForm(UserCreationForm):
    class Meta:
        model = UsuarioPersonalizado
        fields = ['username', 'email', 'telefono', 'password1', 'password2']
    
    def save(self, commit=True):
      user = super().save(commit=False)
      user.is_staff = False
      user.is_superuser = False
      if commit:
          user.save()
      return user
