from django import forms
from .models import Atleta, Entrenador
from django.contrib.auth.models import User
from .constants import CATEGORIAS_COMBATE

CATEGORIA_CHOICES = [(cat, cat) for cat in CATEGORIAS_COMBATE.keys()]
GENERO_CHOICES = [('Femenino', 'Femenino'), ('Masculino', 'Masculino')]

DISCIPLINAS = (
    ('combate', 'Combate'),
    ('poomsae', 'Poomsae'),
)

CATEGORIAS_POOMSAE = (
    ("tradicional", "Tradicional"),
    ("freestyle", "Freestyle"),
    ("ambas", "Ambas"),
)

class AtletaForm(forms.ModelForm):
    disciplina = forms.ChoiceField(choices=DISCIPLINAS, required=True)
    # 👇 AQUI va el campo personalizado de fecha
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento',
        required=True,
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'],  # acepta: 2024-06-15, 15/06/2024, 15-06-2024
        widget=forms.DateInput(
            attrs={
                'type': 'date',  # Calendario visual moderno
                'class': 'form-control',
                'placeholder': 'dd/mm/aaaa',  # Hint
                'autocomplete': 'off',
            },
            format='%Y-%m-%d'  # El que espera el input type=date, pero acepta los otros
        ),
    )
    peso = forms.ChoiceField(choices=[('', 'Seleccione primero categoría y género')], required=False)
    categoria_poomsae = forms.ChoiceField(choices=[('', 'Seleccione una categoría')] + list(CATEGORIAS_POOMSAE), required=False)

    class Meta:
        model = Atleta
        fields = [
            'disciplina',
            'nombre_completo',
            'fecha_nacimiento',
            'cui',
            'genero',
            'cinta',
            'categoria',          # solo combate
            'peso',               # solo combate
            'categoria_poomsae',  # solo poomsae
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = self.data or self.initial
        categoria = data.get('categoria')
        genero = data.get('genero')
        disciplina = data.get('disciplina')
        # Combate: actualiza pesos según categoría/género
        if categoria and genero and categoria in CATEGORIAS_COMBATE and genero in CATEGORIAS_COMBATE[categoria]:
            pesos = CATEGORIAS_COMBATE[categoria][genero]
            self.fields['peso'].choices = [(p, p) for p in pesos]
        else:
            self.fields['peso'].choices = [('', 'Seleccione primero categoría y género')]
        # Oculta los campos según la disciplina
        if disciplina == 'poomsae':
            self.fields['categoria'].required = False
            self.fields['peso'].required = False
            self.fields['categoria_poomsae'].required = True
        else:
            self.fields['categoria'].required = True
            self.fields['peso'].required = True
            self.fields['categoria_poomsae'].required = False

    def clean(self):
        cleaned_data = super().clean()
        disciplina = cleaned_data.get('disciplina')
        categoria = cleaned_data.get('categoria')
        genero = cleaned_data.get('genero')
        peso = cleaned_data.get('peso')
        categoria_poomsae = cleaned_data.get('categoria_poomsae')
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        nombre = cleaned_data.get('nombre_completo')

        if disciplina == 'combate':
            # Validación combate (idéntica a la tuya, solo si es combate)
            from .constants import CATEGORIAS_COMBATE
            if categoria and fecha_nacimiento:
                anio = fecha_nacimiento.year
                rango = CATEGORIAS_COMBATE[categoria]['rango']
                if not (rango[0] <= anio <= rango[1]):
                    self.add_error('fecha_nacimiento', f"El atleta no puede inscribirse en {categoria}. Debe haber nacido entre {rango[0]} y {rango[1]}.")
            if categoria and genero and peso:
                pesos_validos = CATEGORIAS_COMBATE[categoria][genero]
                if peso not in pesos_validos:
                    self.add_error('peso', "El peso seleccionado no corresponde al género y categoría elegidos.")

        if disciplina == 'poomsae':
            # Solo exige categoria_poomsae en poomsae
            if not categoria_poomsae:
                self.add_error('categoria_poomsae', "Selecciona la categoría de poomsae.")

        # Validación advertencia género-nombre (opcional, ahora comentada)
        #if genero == 'femenino' and not any(x in nombre.lower() for x in ['ana', 'maría', 'jack', 'sofía', 'gabriela', 'carla', 'aleja', 'estefany']):
        #    self.add_error('nombre_completo', "Advertencia: el nombre parece no concordar con el género femenino. Verifique.")
        #if genero == 'masculino' and any(x in nombre.lower() for x in ['ana', 'maría', 'jack', 'sofía', 'gabriela', 'carla', 'aleja', 'estefany']):
        #    self.add_error('nombre_completo', "Advertencia: el nombre parece femenino pero el género es masculino. Verifique.")

        return cleaned_data

class RegistroEntrenadorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    username = forms.CharField(max_length=150)

    class Meta:
        model = Entrenador
        fields = ['nombre_completo', 'email', 'gimnasio', 'cui', 'telefono']

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

# Forms de Maestro/Administrador

from django import forms
from django.contrib.auth.models import User
from gestion.models import Maestro

class MaestroRegistroForm(forms.Form):
    nombre_completo = forms.CharField(max_length=100, label="Nombre completo")
    email = forms.EmailField(label="Correo electrónico")
    cui = forms.CharField(max_length=20, label="DPI o CUI")
    telefono = forms.CharField(max_length=15, required=False, label="Teléfono")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    clave_secreta = forms.CharField(widget=forms.PasswordInput, label="Clave de acceso")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        clave = cleaned_data.get("clave_secreta")

        if password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        # Aquí defines la clave que tú vas a compartir
        CLAVE_CORRECTA = "ACCESO2025"

        if clave != CLAVE_CORRECTA:
            raise forms.ValidationError("Clave de acceso inválida. Consulta con el administrador.")

        return cleaned_data
