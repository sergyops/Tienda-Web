from django import forms
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ContactForm(forms.Form):
    name = forms.CharField(label="Nombre", max_length=100)
    email = forms.EmailField(label="Email")
    message = forms.CharField(label="Mensaje", widget=forms.Textarea)

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(label="Correo electrónico", required=True)
    name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)
    address = forms.CharField(label="Dirección", required=True)
    city = forms.CharField(label="Ciudad", required=True)
    postal_code = forms.CharField(label="Código postal", required=True)
    phone = forms.CharField(label="Teléfono", required=True)
    class Meta:
        model = UserProfile
        fields = ['name', 'last_name', 'address', 'city', 'postal_code', 'phone']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está en uso")

        return email