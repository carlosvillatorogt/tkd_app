from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('inscribir/', views.inscribir_atleta, name='inscribir_atleta'),
    path('inscripcion-exitosa/', views.inscripcion_exitosa, name='inscripcion_exitosa'),
    path('registro-entrenador/', views.registro_entrenador, name='registro_entrenador'),
    path('activar-cuenta/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),
    path('mis-atletas/', views.lista_atletas, name='lista_atletas'),
    path('editar-atleta/<int:atleta_id>/', views.editar_atleta, name='editar_atleta'),
    path('borrar-atleta/<int:atleta_id>/', views.borrar_atleta, name='borrar_atleta'),
    path('inscribir-a-torneo/', views.inscribir_a_torneo, name='inscribir_a_torneo'),
    path('inscripcion-torneo-exitosa/', views.inscripcion_torneo_exitosa, name='inscripcion_torneo_exitosa'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('panel-entrenador/', views.panel_entrenador, name='panel_entrenador'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('admin/entrenadores/', views.admin_entrenadores, name='admin_entrenadores'),
    path('ver-torneos/', views.ver_torneos, name='ver_torneos'),
    path('atletas-ranking/', views.atletas_ranking, name='atletas_ranking'),
    path('registro-maestro/', views.registro_maestro, name='registro_maestro'),
    path('login-maestro/', views.login_maestro, name='login_maestro'),
    path('panel-maestro/', views.panel_maestro, name='panel_maestro'),
    path('registro-exitoso-maestro/', views.registro_exitoso_maestro, name='registro_exitoso_maestro'),

]
