from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario
from rest_framework import viewsets
from .models import (
    Usuario, Mascota, Vacuna, MascotaVacuna, Cita, 
    ComposicionConsulta, ObservacionSintoma, EvaluacionDiagnostico,
    Tratamiento, AccionTratamiento, Receta, ChatbotConsulta, LogAcceso
)
from .serializers import (
    UsuarioSerializer, MascotaSerializer, VacunaSerializer, MascotaVacunaSerializer,
    CitaSerializer, ComposicionConsultaSerializer, ObservacionSintomaSerializer,
    EvaluacionDiagnosticoSerializer, TratamientoSerializer, AccionTratamientoSerializer,
    RecetaSerializer, ChatbotConsultaSerializer, LogAccesoSerializer
)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.all()
    serializer_class = MascotaSerializer

class VacunaViewSet(viewsets.ModelViewSet):
    queryset = Vacuna.objects.all()
    serializer_class = VacunaSerializer

class MascotaVacunaViewSet(viewsets.ModelViewSet):
    queryset = MascotaVacuna.objects.all()
    serializer_class = MascotaVacunaSerializer

class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer

class ComposicionConsultaViewSet(viewsets.ModelViewSet):
    queryset = ComposicionConsulta.objects.all()
    serializer_class = ComposicionConsultaSerializer

class ObservacionSintomaViewSet(viewsets.ModelViewSet):
    queryset = ObservacionSintoma.objects.all()
    serializer_class = ObservacionSintomaSerializer

class EvaluacionDiagnosticoViewSet(viewsets.ModelViewSet):
    queryset = EvaluacionDiagnostico.objects.all()
    serializer_class = EvaluacionDiagnosticoSerializer

class TratamientoViewSet(viewsets.ModelViewSet):
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer

class AccionTratamientoViewSet(viewsets.ModelViewSet):
    queryset = AccionTratamiento.objects.all()
    serializer_class = AccionTratamientoSerializer

class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer

class ChatbotConsultaViewSet(viewsets.ModelViewSet):
    queryset = ChatbotConsulta.objects.all()
    serializer_class = ChatbotConsultaSerializer

class LogAccesoViewSet(viewsets.ModelViewSet):
    queryset = LogAcceso.objects.all()
    serializer_class = LogAccesoSerializer


@api_view(['POST'])
def login_usuario(request):
    email = request.data.get('email')
    contraseña = request.data.get('contraseña')

    try:
        usuario = Usuario.objects.get(email=email)
        if usuario.contraseña_hash == contraseña:
            return Response({
                'id': usuario.id,
                'nombre_completo': usuario.nombre_completo,
                'email': usuario.email,
                'rol': usuario.rol,
                'fotografia': usuario.fotografia
            })
        else:
            return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)