from django.contrib import admin
from .models import Atleta

admin.site.register(Atleta)

from .models import Torneo

admin.site.register(Torneo)

from .models import Entrenador

admin.site.register(Entrenador)

from .models import Inscripcion

admin.site.register(Inscripcion)

from .models import Combate

admin.site.register(Combate)

from .models import Ranking

admin.site.register(Ranking)

from django.contrib import admin
from .models import Maestro

@admin.register(Maestro)
class MaestroAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'email', 'aprobado')
    list_filter = ('aprobado',)
    search_fields = ('nombre_completo', 'email', 'cui')
