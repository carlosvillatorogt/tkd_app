from django.db import models
from django.contrib.auth.models import User

class Atleta(models.Model):
    entrenador = models.ForeignKey('Entrenador', on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    cui = models.CharField("CUI o Pasaporte", max_length=20, unique=True)
    genero = models.CharField(max_length=10, choices=[
        ("masculino", "Masculino"),
        ("femenino", "Femenino"),
    ])
    cinta = models.CharField(max_length=10, choices=[
        ("blanca", "Blanca"),
        ("amarilla", "Amarilla"),
        ("verde", "Verde"),
        ("azul", "Azul"),
        ("roja", "Roja"),
        ("negra", "Negra"),
    ])
    categoria = models.CharField(max_length=10, choices=[
        ("cadete", "Cadete"),
        ("juvenil", "Juvenil"),
        ("adulto", "Adulto"),
    ])
    peso = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre_completo

class Torneo(models.Model):
    TIPO_TORNEO = [
        ('general', 'General'),
        ('combate', 'Combate'),
        ('poomsae', 'Poomsae'),
        ('departamental', 'Departamental'),
        ('ranking', 'Ranking'),
        ('nacional', 'Nacional'),
    ]

    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    lugar = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_TORNEO)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Inscripcion(models.Model):
    atleta = models.ForeignKey('Atleta', on_delete=models.CASCADE)
    torneo = models.ForeignKey('Torneo', on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ], default='pendiente')

    def __str__(self):
        return f"{self.atleta} - {self.torneo}"

#class Entrenador(models.Model):
#    nombre_completo = models.CharField(max_length=100)
#    email = models.EmailField(unique=True)
#    gimnasio = models.CharField(max_length=100)
#    cui = models.CharField("DPI o CUI del Entrenador", max_length=20, unique=True)
#    telefono = models.CharField(max_length=15, blank=True, null=True)

#    def __str__(self):
#        return self.nombre_completo

class Entrenador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación con el usuario Django
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    gimnasio = models.CharField(max_length=100)
    cui = models.CharField("DPI o CUI del Entrenador", max_length=20, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nombre_completo

class Combate(models.Model):
    torneo = models.ForeignKey('Torneo', on_delete=models.CASCADE)
    atleta_azul = models.ForeignKey('Atleta', on_delete=models.CASCADE, related_name='combates_azul')
    atleta_rojo = models.ForeignKey('Atleta', on_delete=models.CASCADE, related_name='combates_rojo')
    ganador = models.ForeignKey('Atleta', on_delete=models.CASCADE, related_name='combates_ganados', null=True, blank=True)
    ronda = models.CharField(max_length=20, default="Primera ronda")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.torneo}: {self.atleta_azul} vs {self.atleta_rojo} ({self.ronda})"

class Ranking(models.Model):
    atleta = models.ForeignKey('Atleta', on_delete=models.CASCADE)
    puntos = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    torneo = models.ForeignKey('Torneo', on_delete=models.CASCADE)
    posicion = models.PositiveIntegerField()
    categoria_g = models.CharField(max_length=5, choices=[
        ('G1', 'G1'),
        ('G2', 'G2'),
        ('G4', 'G4'),
    ], default='G1')

    def __str__(self):
        return f"{self.atleta} - {self.puntos} puntos ({self.torneo})"
