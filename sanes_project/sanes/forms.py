from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile  # Asegúrate de importar tu modelo UserProfile
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Correo Electrónico o Usuario", max_length=254)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def clean_username(self):
        username_or_email = self.cleaned_data['username']
        return username_or_email  # No es necesario hacer validaciones adicionales aquí

class CustomUserCreationForm(UserCreationForm):
    cedula = forms.CharField(max_length=20, required=True, label="Cédula")
    oficio = forms.CharField(max_length=100, required=True, label="Oficio")
    telefono = forms.CharField(max_length=15, required=True, label="Teléfono")
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'cedula', 'oficio', 'telefono']

    def save(self, commit=True):
        user = super().save(commit)
        user.email = self.cleaned_data['email']  # Asigna el correo electrónico al usuario
        if commit:
            user.save()  # Guarda el usuario
        # Crear el perfil del usuario sin el email
        UserProfile.objects.create(
            user=user,
            cedula=self.cleaned_data['cedula'],
            oficio=self.cleaned_data['oficio'],
            telefono=self.cleaned_data['telefono']
        )
        return user

from django import forms

class ConfirmPurchaseForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Transferencia Bancaria'),
        ('cash', 'Efectivo'),
    ]
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect)
    payment_receipt = forms.ImageField(required=False, help_text="Sube una captura del pago si seleccionas transferencia bancaria.")

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method")
        payment_receipt = cleaned_data.get("payment_receipt")

        # Verificar que la captura de pantalla esté presente si se selecciona transferencia bancaria
        if payment_method == 'bank_transfer' and not payment_receipt:
            raise forms.ValidationError("Debes subir una captura del pago para transferencia bancaria.")

from django import forms
from .models import San

class SanForm(forms.ModelForm):
    class Meta:
        model = San
        fields = [
            'name', 
            'organizador', 
            'fecha_inicio', 
            'total_price', 
            'num_cuotas', 
            'payment_frequency', 
            'type_of_san', 
            'image', 
            'total_participantes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del SAN o Producto'}),
            'organizador': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio Total'}),
            'num_cuotas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de Cuotas'}),
            'payment_frequency': forms.Select(attrs={'class': 'form-control'}),
            'type_of_san': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'total_participantes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total de Participantes'}),
        }
