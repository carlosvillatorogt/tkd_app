from django import forms
from .models import Atleta
from django import forms
from django.contrib.auth.models import User
from .models import Entrenador

from .constants import CATEGORIAS_COMBATE   # <--- importa esto

CATEGORIA_CHOICES = [(cat, cat) for cat in CATEGORIAS_COMBATE.keys()]
GENERO_CHOICES = [('Femenino', 'Femenino'), ('Masculino', 'Masculino')]

class AtletaForm(forms.ModelForm):
    peso = forms.ChoiceField(choices=[('', 'Seleccione primero categoría y género')])

    class Meta:
        model = Atleta
        fields = [
            'nombre_completo',
            'fecha_nacimiento',
            'cui',
            'genero',
            'cinta',
            'categoria',
            'peso'
        ]  # <-- ya NO incluyas 'entrenador'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        data = self.data or self.initial
        categoria = data.get('categoria')
        genero = data.get('genero')
        if categoria and genero and categoria in CATEGORIAS_COMBATE and genero in CATEGORIAS_COMBATE[categoria]:
            pesos = CATEGORIAS_COMBATE[categoria][genero]
            self.fields['peso'].choices = [(p, p) for p in pesos]
        else:
            self.fields['peso'].choices = [('', 'Seleccione primero categoría y género')]

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        genero = cleaned_data.get('genero')
        peso = cleaned_data.get('peso')
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        nombre = cleaned_data.get('nombre_completo')

        # Validación año de nacimiento
        from .constants import CATEGORIAS_COMBATE
        if categoria and fecha_nacimiento:
            anio = fecha_nacimiento.year
            rango = CATEGORIAS_COMBATE[categoria]['rango']
            if not (rango[0] <= anio <= rango[1]):
                self.add_error('fecha_nacimiento', f"El atleta no puede inscribirse en {categoria}. Debe haber nacido entre {rango[0]} y {rango[1]}.")

        # Validación peso
        if categoria and genero and peso:
            pesos_validos = CATEGORIAS_COMBATE[categoria][genero]
            if peso not in pesos_validos:
                self.add_error('peso', "El peso seleccionado no corresponde al género y categoría elegidos.")

        # (Opcional) Validación advertencia género-nombre (simple)
        if genero == 'femenino' and not any(x in nombre.lower() for x in ['ana', 'maría', 'jack', 'sofía', 'gabriela', 'carla', 'aleja', 'estefany']):
            self.add_error('nombre_completo', "Advertencia: el nombre parece no concordar con el género femenino. Verifique.")
        if genero == 'masculino' and any(x in nombre.lower() for x in ['ana', 'maría', 'jack', 'sofía', 'gabriela', 'carla', 'aleja', 'estefany']):
            self.add_error('nombre_completo', "Advertencia: el nombre parece femenino pero el género es masculino. Verifique.")
        return cleaned_data

#class AtletaForm(forms.ModelForm):
#    class Meta:
#        model = Atleta
#        fields = ['entrenador', 'nombre_completo', 'fecha_nacimiento', 'cui', 'genero', 'cinta', 'categoria', 'peso']

class RegistroEntrenadorForm(forms.ModelForm):
    # Campo de contraseña para el usuario
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Entrenador
        fields = ['nombre_completo', 'email', 'gimnasio', 'cui', 'telefono']

    # Campos del usuario extra
    username = forms.CharField(max_length=150)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese correo.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre de usuario.")
        return username