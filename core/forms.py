from django import forms
<<<<<<< HEAD
=======
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioPersonalizado
>>>>>>> 4a0f18c3d850a59a49289a69804614ac2703d9b7

class LoginForm(forms.Form):
    usuario = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)

<<<<<<< HEAD
# class RegistroUsuarioForm(UserCreationForm):
#     class Meta:
#         model = UsuarioPersonalizado
#         fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
=======
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
>>>>>>> 4a0f18c3d850a59a49289a69804614ac2703d9b7
