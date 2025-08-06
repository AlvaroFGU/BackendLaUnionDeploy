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
]
