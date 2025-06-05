from django import forms

class LoginForm(forms.Form):
    usuario = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)

# class RegistroUsuarioForm(UserCreationForm):
#     class Meta:
#         model = UsuarioPersonalizado
#         fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']