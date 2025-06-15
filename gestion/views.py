#from django.shortcuts import render

# Create your views here.

# Vista de Registro formulario Entrenador
from django.contrib.auth.models import User
from .forms import RegistroEntrenadorForm
from .models import Entrenador
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404

from django.shortcuts import render, redirect
from .forms import AtletaForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

import json
from .constants import CATEGORIAS_COMBATE
from .forms import AtletaForm

@login_required
def inscribir_atleta(request):
    entrenador = Entrenador.objects.get(user=request.user)
    if request.method == 'POST':
        form = AtletaForm(request.POST)
        if form.is_valid():
            atleta = form.save(commit=False)
            atleta.entrenador = entrenador  # siempre asigna el entrenador logueado
            atleta.save()
            return redirect('inscripcion_exitosa')
        else:
            print("ERRORES DEL FORMULARIO:", form.errors)   # <-- AGREGA ESTO PARA DEBUG
    else:
        form = AtletaForm()
    # Pasa entrenador para mostrarlo en la plantilla
    return render(request, 'inscripcion_atleta.html', {
        'form': form,
        'entrenador': entrenador,
        'categorias_json': json.dumps(CATEGORIAS_COMBATE)
    })

def inscripcion_exitosa(request):
    return render(request, 'inscripcion_exitosa.html')

# Logica del formulario de registro entrenador
def registro_entrenador(request):
    if request.method == 'POST':
        form = RegistroEntrenadorForm(request.POST)
        if form.is_valid():
            # Crear usuario inactivo
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                is_active=False # inactivo hasta que confirme email
            )
            # Crear perfil de entrenador
            entrenador = form.save(commit=False)
            entrenador.user = user
            entrenador.save()

            # Enviar correo de activación
            current_site = get_current_site(request)
            subject = 'Activa tu cuenta de entrenador'
            message = render_to_string('activacion_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return render(request, 'registro_exitoso.html')
    else:
        form = RegistroEntrenadorForm()
    return render(request, 'registro_entrenador.html', {'form': form})

def activar_cuenta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'activacion_exitosa.html')
    else:
        return HttpResponse('El enlace de activación no es válido.')

# Vista para listar atletas del entrenador

from django.contrib.auth.decorators import login_required
from .models import Atleta, Entrenador

@login_required
def lista_atletas(request):
    entrenador = Entrenador.objects.get(user=request.user)
    atletas = Atleta.objects.filter(entrenador=entrenador)
    return render(request, 'lista_atletas.html', {
        'atletas': atletas,
        'entrenador': entrenador,
    })

@login_required
def editar_atleta(request, atleta_id):
    entrenador = Entrenador.objects.get(user=request.user)
    atleta = get_object_or_404(Atleta, id=atleta_id, entrenador=entrenador)
    if request.method == 'POST':
        form = AtletaForm(request.POST, instance=atleta)
        if form.is_valid():
            atleta = form.save(commit=False)
            atleta.entrenador = entrenador  # asegura que nunca se cambie el entrenador
            atleta.save()
            return redirect('lista_atletas')
    else:
        form = AtletaForm(instance=atleta)
    return render(request, 'editar_atleta.html', {
        'form': form,
        'entrenador': entrenador,
        'categorias_json': json.dumps(CATEGORIAS_COMBATE)
    })

@login_required
def borrar_atleta(request, atleta_id):
    entrenador = Entrenador.objects.get(user=request.user)
    atleta = get_object_or_404(Atleta, id=atleta_id, entrenador=entrenador)
    if request.method == 'POST':
        atleta.delete()
        return redirect('lista_atletas')
    return render(request, 'borrar_atleta.html', {
        'atleta': atleta,
        'entrenador': entrenador,
    })

# Inscripción de atletas a torneos activos
from .models import Torneo, Inscripcion

@login_required
def inscribir_a_torneo(request):
    entrenador = Entrenador.objects.get(user=request.user)
    atletas = Atleta.objects.filter(entrenador=entrenador)
    torneos = Torneo.objects.all()  # puedes filtrar solo torneos activos si agregas un campo 'activo' a Torneo

    if request.method == 'POST':
        atleta_id = request.POST.get('atleta')
        torneo_id = request.POST.get('torneo')
        if atleta_id and torneo_id:
            atleta = Atleta.objects.get(id=atleta_id, entrenador=entrenador)
            torneo = Torneo.objects.get(id=torneo_id)
            # Evita duplicados
            if not Inscripcion.objects.filter(atleta=atleta, torneo=torneo).exists():
                Inscripcion.objects.create(atleta=atleta, torneo=torneo)
            return redirect('inscripcion_torneo_exitosa')

    return render(request, 'inscribir_a_torneo.html', {'atletas': atletas, 'torneos': torneos})

def inscripcion_torneo_exitosa(request):
    return render(request, 'inscripcion_torneo_exitosa.html')

# Paneles de Administración

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Entrenador

@login_required
def panel_entrenador(request):
    entrenador = Entrenador.objects.get(user=request.user)
    return render(request, 'panel_entrenador.html', {'entrenador': entrenador})

@login_required
def panel_admin(request):
    # Puedes pasar más contexto si lo deseas
    return render(request, 'panel_admin.html')


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_entrenadores(request):
    query = request.GET.get('q', '')
    from .models import Entrenador
    if query:
        entrenadores = Entrenador.objects.filter(nombre_completo__icontains=query)
    else:
        entrenadores = Entrenador.objects.all()
    return render(request, 'admin_entrenadores.html', {'entrenadores': entrenadores, 'request': request})


from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'login.html'  # Usa el nombre de tu template de login

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return reverse_lazy('panel_admin')
        else:
            return reverse_lazy('panel_entrenador')

@login_required
def ver_torneos(request):
    # Aquí luego puedes mostrar la lista de torneos
    return render(request, 'ver_torneos.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Atleta

@login_required
def atletas_ranking(request):
    atletas = Atleta.objects.filter(puntos_ranking__gt=0).order_by('-puntos_ranking')
    return render(request, 'atletas_ranking.html', {'atletas': atletas})

