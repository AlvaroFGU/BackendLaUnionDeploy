from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Usuario
import random
from django.core.mail import send_mail
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
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
from rest_framework_simplejwt.views import TokenObtainPairView
from gestion_clinica.serializers import CustomTokenObtainPairSerializer

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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
def login_usuario(request):
    email = request.data.get('email')
    contrasenia = request.data.get('contrasenia')

    try:
        usuario = Usuario.objects.get(email=email)

        if usuario.contrasenia_hash == contrasenia:
            refresh = RefreshToken.for_user(usuario)

            return Response({
                'id_usuario': usuario.id_usuario,
                'nombre_completo': usuario.nombre_completo,
                'email': usuario.email,
                'rol': usuario.rol,
                'fotografia': usuario.fotografia,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })

        else:
            return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def enviar_codigo(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email requerido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(email=email)
        codigo = str(random.randint(100000, 999999))
        usuario.codigo = codigo
        usuario.save()

        asunto = 'Código de recuperación de contraseña'
        mensaje = f'Hola {usuario.nombre_completo},\n\nTu código de recuperación es: {codigo}'
        remitente = None  # toma el DEFAULT_FROM_EMAIL
        destinatarios = [email]

        send_mail(asunto, mensaje, remitente, destinatarios)

        return Response({'mensaje': 'Código enviado al correo.'})
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def confirmar_cambio(request):
    email = request.data.get('email')
    codigo = request.data.get('codigo')
    nueva_contrasenia = request.data.get('contrasenia')

    if not all([email, codigo, nueva_contrasenia]):
        return Response({'error': 'Todos los campos son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(email=email, codigo=codigo)
        usuario.contrasenia_hash = nueva_contrasenia  # o hasheada si luego usas auth real
        usuario.codigo = None  # Limpia el código
        usuario.save()
        return Response({'mensaje': 'Contraseña actualizada correctamente'})
    except Usuario.DoesNotExist:
        return Response({'error': 'Código inválido o usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)