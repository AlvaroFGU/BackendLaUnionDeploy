"""
URL configuration for veterinaria project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from gestion_clinica.views import login_usuario
from gestion_clinica.views import confirmar_cambio
from gestion_clinica.views import enviar_codigo
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import routers
from gestion_clinica.views import (
    UsuarioViewSet, MascotaViewSet, VacunaViewSet, MascotaVacunaViewSet,
    CitaViewSet, ComposicionConsultaViewSet, ObservacionSintomaViewSet,
    EvaluacionDiagnosticoViewSet, TratamientoViewSet, AccionTratamientoViewSet,
    RecetaViewSet, ChatbotConsultaViewSet, LogAccesoViewSet
)

from gestion_clinica.views import *

router = routers.DefaultRouter()
router.register('usuarios', UsuarioViewSet)
router.register('mascotas', MascotaViewSet)
router.register('vacunas', VacunaViewSet)
router.register('mascotas-vacunas', MascotaVacunaViewSet)
router.register('citas', CitaViewSet)
router.register('consultas', ComposicionConsultaViewSet)
router.register('sintomas', ObservacionSintomaViewSet)
router.register('diagnosticos', EvaluacionDiagnosticoViewSet)
router.register('tratamientos', TratamientoViewSet)
router.register('acciones-tratamientos', AccionTratamientoViewSet)
router.register('recetas', RecetaViewSet)
router.register('chatbot', ChatbotConsultaViewSet)
router.register('logs', LogAccesoViewSet)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', login_usuario),
    path('api/enviar-codigo/', enviar_codigo, name='enviar_codigo'),
    path('api/confirmar-cambio/', confirmar_cambio, name='confirmar_cambio'),
    path('api/clientes/', listar_clientes, name='listar_clientes'),
    path('api/clientes/crear/', crear_cliente, name='crear_cliente'),
    path('api/clientes/<int:id_usuario>/', ver_cliente, name='ver_cliente'),
    path('api/clientes/<int:id_usuario>/editar/', editar_cliente, name='editar_cliente'),
    path('api/clientes/<int:id_usuario>/eliminar/', eliminar_cliente, name='eliminar_cliente'),
    path('api/mascota/', listar_mascotas, name='listar_mascotas'),
    path('api/mascota/<int:id_usuario>/', listar_mascotas_cliente, name='listar_mascotas_cliente'),
    path('api/mascota/<int:id_mascota>/', ver_mascota, name='ver_mascota'),
    path('api/mascota/crear/', crear_mascota, name='crear_mascota'),
    path('api/mascota/<int:id_mascota>/editar/', editar_mascota, name='editar_mascota'),
    path('api/mascota/<int:id_mascota>/eliminar/', eliminar_mascota, name='eliminar_mascota'),
    path('api/vacuna/', listar_vacunas, name='listar_vacunas'),
    path('api/vacuna/<int:id_vacuna>/', ver_vacuna, name='ver_vacuna'),
    path('api/vacuna/nombre/<str:nombre>/', ver_vacuna_nombre, name='ver_vacuna_nombre'),
    path('api/vacuna/crear/', crear_vacuna, name='crear_vacuna'),
    path('api/vacuna/<int:id_vacuna>/editar/', editar_vacuna, name='editar_vacuna'),
    path('api/vacuna/<int:id_vacuna>/eliminar/', eliminar_vacuna, name='eliminar_vacuna'),
    path('api/vacuna/<int:id_vacuna>/habilitar/', habilitar_vacuna, name='habilitar_vacuna'),
    path('api/mascota_vacuna/', listar_mascota_vacunas, name='listar_mascota_vacunas'),
    path('api/mascota_vacuna/mascota/<int:id_mascota>/', listar_mascota_vacunas_por_mascota, name='listar_mascota_vacunas_por_mascota'),
    path('api/mascota_vacuna/veterinario/<int:id_veterinario>/', listar_mascota_vacunas_por_veterinario, name='listar_mascota_vacunas_por_veterinario'),
    path('api/mascota_vacuna/<int:id_mascota_vacuna>/', ver_mascota_vacuna, name='ver_mascota_vacuna'),
    path('api/mascota_vacuna/crear/', crear_mascota_vacuna, name='crear_mascota_vacuna'),
    path('api/mascota_vacuna/<int:id_mascota_vacuna>/editar/', editar_mascota_vacuna, name='editar_mascota_vacuna'),
    path('api/mascota_vacuna/<int:id_mascota_vacuna>/eliminar/', eliminar_mascota_vacuna, name='eliminar_mascota_vacuna'),
    path('api/cita/', listar_citas, name='listar_citas'),
    path('api/cita/mascota/<int:id_mascota>/', listar_citas_por_mascota, name='listar_citas_por_mascota'),
    path('api/cita/veterinario/<int:id_veterinario>/', listar_citas_por_veterinario, name='listar_citas_por_veterinario'),
    path('api/cita/<int:id_cita>/', ver_cita, name='ver_cita'),
    path('api/cita/crear/', crear_cita, name='crear_cita'),
    path('api/cita/<int:id_cita>/editar/', editar_cita, name='editar_cita'),
    path('api/cita/<int:id_cita>/eliminar/', eliminar_cita, name='eliminar_cita'),
    path('api/tratamiento/', listar_tratamientos, name='listar_tratamientos'),
    path('api/tratamiento/<int:id_tratamiento>/', ver_tratamiento, name='ver_tratamiento'),
    path('api/tratamiento/crear/', crear_tratamiento, name='crear_tratamiento'),
    path('api/tratamiento/<int:id_tratamiento>/editar/', editar_tratamiento, name='editar_tratamiento'),
    path('api/tratamiento/<int:id_tratamiento>/eliminar/', eliminar_tratamiento, name='eliminar_tratamiento'),
    path('api/personal/', listar_personal, name='listar_personal'),
    path('api/personal/<int:id_personal>/', ver_personal, name='ver_personal'),
    path('api/personal/crear/', crear_personal, name='crear_personal'),
    path('api/personal/<int:id_personal>/editar/', editar_personal, name='editar_personal'),
    path('api/personal/<int:id_personal>/eliminar/', eliminar_personal, name='eliminar_personal'),
]
