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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone
from .serializers import ClienteSerializer
from .utils import registrar_log
import hashlib


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
    

#Crear Cliente 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_cliente(request):
    data = request.data.copy()
    data['rol'] = 'cliente'
    data['estado'] = True
    data['codigo'] = '-99'
    data['contrasenia_hash'] = hashlib.sha256((data['ci'] + "VetLaUnion").encode()).hexdigest()

    serializer = ClienteSerializer(data=data)
    if serializer.is_valid():
        cliente = serializer.save()
        registrar_log(request.user.id_usuario, "Cliente", "crear", cliente.id_usuario)
        return Response({"mensaje": "Cliente creado exitosamente."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Listar clientes activos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_clientes(request):
    id_usuario_log = request.query_params.get('id_usuario', None)

    clientes = Usuario.objects.filter(rol='cliente', estado=True)
    serializer = ClienteSerializer(clientes, many=True)
    return Response(serializer.data)


# Ver cliente por ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_cliente(request, id_usuario):
    try:
        cliente = Usuario.objects.get(id_usuario=id_usuario, rol='cliente')
    except Usuario.DoesNotExist:
        return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ClienteSerializer(cliente)
    registrar_log(request.user.id_usuario, "Cliente", "ver", id_usuario)
    return Response(serializer.data)


# Editar cliente
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def editar_cliente(request, id_usuario):
    try:
        cliente = Usuario.objects.get(id_usuario=id_usuario, rol='cliente')
    except Usuario.DoesNotExist:
        return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ClienteSerializer(cliente, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        registrar_log(request.user.id_usuario, "Cliente", "editar", id_usuario)
        return Response({"mensaje": "Cliente actualizado exitosamente."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Eliminar cliente (lógico)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_cliente(request, id_usuario):
    try:
        cliente = Usuario.objects.get(id_usuario=id_usuario, rol='cliente')
    except Usuario.DoesNotExist:
        return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    cliente.estado = False
    cliente.save()
    registrar_log(request.user.id_usuario, "Cliente", "eliminar", id_usuario)
    return Response({"mensaje": "Cliente eliminado correctamente."})


# Listar todas las mascotas activas
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mascotas(request):
    mascotas = Mascota.objects.filter(estado=True)
    serializer = MascotaSerializer(mascotas, many=True)
    return Response(serializer.data)


# Listar mascotas de un cliente específico
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mascotas_cliente(request, id_usuario):
    mascotas = Mascota.objects.filter(propietario_id=id_usuario, estado=True)
    serializer = MascotaSerializer(mascotas, many=True)
    return Response(serializer.data)


# Ver mascota por ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_mascota(request, id_mascota):
    try:
        mascota = Mascota.objects.get(id_mascota=id_mascota, estado=True)
    except Mascota.DoesNotExist:
        return Response({"error": "Mascota no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MascotaSerializer(mascota)
    registrar_log(request.user.id_usuario, "Mascota", "ver", id_mascota)
    return Response(serializer.data)


# Crear mascota
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_mascota(request):
    serializer = MascotaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        registrar_log(request.user.id_usuario, "Mascota", "crear", "")
        return Response({"mensaje": "Mascota registrada correctamente."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Editar mascota
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def editar_mascota(request, id_mascota):
    try:
        mascota = Mascota.objects.get(id_mascota=id_mascota, estado=True)
    except Mascota.DoesNotExist:
        return Response({"error": "Mascota no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MascotaSerializer(mascota, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        registrar_log(request.user.id_usuario, "Mascota", "editar", id_mascota)
        return Response({"mensaje": "Mascota actualizada correctamente."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Eliminar mascota (marcar como inactiva)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_mascota(request, id_mascota):
    try:
        mascota = Mascota.objects.get(id_mascota=id_mascota, estado=True)
    except Mascota.DoesNotExist:
        return Response({"error": "Mascota no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    mascota.estado = False
    mascota.save()
    registrar_log(request.user.id_usuario, "Mascota", "eliminar", id_mascota)
    return Response({"mensaje": "Mascota eliminada correctamente."}, status=status.HTTP_200_OK)