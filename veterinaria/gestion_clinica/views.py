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
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


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

        if check_password(contrasenia, usuario.contrasenia_hash) and usuario.intentos_sesion < 5:
            usuario.intentos_sesion = 0
            usuario.save()

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
            usuario.intentos_sesion += 1
            usuario.save()

            if usuario.intentos_sesion == 5:
                asunto = 'Advertencia de actividad sospechosa'
                mensaje = f'Hola {usuario.nombre_completo},\n\nSe alcanzó el límite de intentos fallidos de inicio de sesion permitidos por lo que su cuenta ha sido bloqueada, cambia tu contraseña o comunicate con el personal'
                remitente = None 
                destinatarios = [email]

                send_mail(asunto, mensaje, remitente, destinatarios)
                return Response(
                    {'error': 'Cuenta bloqueada por demasiados intentos fallidos'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response(
                {'error': 'Contraseña incorrecta', 'intentos': usuario.intentos_sesion},
                status=status.HTTP_401_UNAUTHORIZED
            )

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
        usuario.contrasenia_hash = make_password(nueva_contrasenia)  
        usuario.codigo = None
        usuario.intentos_sesion = 0
  
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
    data['contrasenia_hash'] = make_password(data['ci'] + "VetLaUnion")

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
        mascota = serializer.save()
        registrar_log(request.user.id_usuario, "Mascota", "crear", mascota.id_mascota)
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


# Listar vacunas
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_vacunas(request):
    vacunas = Vacuna.objects.filter(estado=True)
    serializer = VacunaSerializer(vacunas, many=True)
    return Response(serializer.data)

# Ver vacuna por ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_vacuna(request, id_vacuna):
    try:
        vacuna = Vacuna.objects.get(id_vacuna=id_vacuna)
    except Vacuna.DoesNotExist:
        return Response({"error": "Vacuna no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = VacunaSerializer(vacuna)
    registrar_log(request.user.id_usuario, "Vacuna", "ver", id_vacuna)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_vacuna_nombre(request, nombre):
    try:
        vacuna = Vacuna.objects.get(nombre_vacuna__iexact=nombre)
    except Vacuna.DoesNotExist:
        return Response({"error": "Vacuna no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = VacunaSerializer(vacuna)
    registrar_log(request.user.id_usuario, "Vacuna", "ver", vacuna.id_vacuna)
    return Response(serializer.data)

# Crear vacuna
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_vacuna(request):
    serializer = VacunaSerializer(data=request.data)
    if serializer.is_valid():
        vacuna = serializer.save()
        registrar_log(request.user.id_usuario, "Vacuna", "crear", vacuna.id_vacuna)
        return Response({"mensaje": "Vacuna registrada correctamente."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Editar vacuna
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def editar_vacuna(request, id_vacuna):
    try:
        vacuna = Vacuna.objects.get(id_vacuna=id_vacuna, estado=True)
    except Vacuna.DoesNotExist:
        return Response({"error": "Vacuna no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = VacunaSerializer(vacuna, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        registrar_log(request.user.id_usuario, "Vacuna", "editar", id_vacuna)
        return Response({"mensaje": "Vacuna actualizada correctamente."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Eliminar vacuna (cambio de estado a False)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_vacuna(request, id_vacuna):
    try:
        vacuna = Vacuna.objects.get(id_vacuna=id_vacuna, estado=True)
    except Vacuna.DoesNotExist:
        return Response({"error": "Vacuna no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    vacuna.estado = False
    vacuna.save()
    registrar_log(request.user.id_usuario, "Vacuna", "eliminar", id_vacuna)
    return Response({"mensaje": "Vacuna eliminada correctamente."}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def habilitar_vacuna(request, id_vacuna):
    try:
        vacuna = Vacuna.objects.get(id_vacuna=id_vacuna, estado=False)
    except Vacuna.DoesNotExist:
        return Response({"error": "Vacuna no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    vacuna.estado = True
    vacuna.save()
    registrar_log(request.user.id_usuario, "Vacuna", "eliminar", id_vacuna)
    return Response({"mensaje": "Vacuna habilitada correctamente."}, status=status.HTTP_200_OK)

# Listar todas mascota_vacuna
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mascota_vacunas(request):
    vacunas = MascotaVacuna.objects.filter(estado=True)
    serializer = MascotaVacunaSerializer(vacunas, many=True)
    return Response(serializer.data)

# Listar por mascota
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mascota_vacunas_por_mascota(request, id_mascota):
    vacunas = MascotaVacuna.objects.filter(mascota_id=id_mascota, estado=True)
    serializer = MascotaVacunaSerializer(vacunas, many=True)
    return Response(serializer.data)

# Listar por veterinario
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_mascota_vacunas_por_veterinario(request, id_veterinario):
    vacunas = MascotaVacuna.objects.filter(veterinario_id=id_veterinario, estado=True)
    serializer = MascotaVacunaSerializer(vacunas, many=True)
    return Response(serializer.data)

# Ver por ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_mascota_vacuna(request, id_mascota_vacuna):
    try:
        registro = MascotaVacuna.objects.get(id_mascota_vacuna=id_mascota_vacuna)
    except MascotaVacuna.DoesNotExist:
        return Response({"error": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    serializer = MascotaVacunaSerializer(registro)
    return Response(serializer.data)

# Crear
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_mascota_vacuna(request):
    serializer = MascotaVacunaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Vacuna registrada para la mascota correctamente."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Editar
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def editar_mascota_vacuna(request, id_mascota_vacuna):
    try:
        registro = MascotaVacuna.objects.get(id_mascota_vacuna=id_mascota_vacuna)
    except MascotaVacuna.DoesNotExist:
        return Response({"error": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MascotaVacunaSerializer(registro, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Registro de vacuna actualizado correctamente."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Eliminar (cambia estado a false)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_mascota_vacuna(request, id_mascota_vacuna):
    try:
        registro = MascotaVacuna.objects.get(id_mascota_vacuna=id_mascota_vacuna)
    except MascotaVacuna.DoesNotExist:
        return Response({"error": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    registro.estado = False
    registro.save()
    return Response({"mensaje": "Registro de vacuna eliminado correctamente."}, status=status.HTTP_200_OK)

# Listar todas las citas
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_citas(request):
    citas = Cita.objects.filter(estado=True)
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data)

# Listar por mascota
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_citas_por_mascota(request, id_mascota):
    citas = Cita.objects.filter(mascota_id=id_mascota, estado=True)
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data)

# Listar por veterinario
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_citas_por_veterinario(request, id_veterinario):
    citas = Cita.objects.filter(veterinario_id=id_veterinario, estado=True)
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data)

# Ver por ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_cita(request, id_cita):
    try:
        cita = Cita.objects.get(id_cita=id_cita)
    except Cita.DoesNotExist:
        return Response({"error": "Cita no encontrada"}, status=status.HTTP_404_NOT_FOUND)
    serializer = CitaSerializer(cita)
    return Response(serializer.data)

# Crear cita
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_cita(request):
    serializer = CitaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Cita creada correctamente."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Editar cita
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def editar_cita(request, id_cita):
    try:
        cita = Cita.objects.get(id_cita=id_cita)
    except Cita.DoesNotExist:
        return Response({"error": "Cita no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CitaSerializer(cita, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Cita actualizada correctamente."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Eliminar (cambia estado a false)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_cita(request, id_cita):
    try:
        cita = Cita.objects.get(id_cita=id_cita)
    except Cita.DoesNotExist:
        return Response({"error": "Cita no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    cita.estado = False
    cita.save()
    return Response({"mensaje": "Cita eliminada correctamente."}, status=status.HTTP_200_OK)

# Listar tratamientos activos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_tratamientos(request):
    tratamientos = Tratamiento.objects.filter(estado=True)
    serializer = TratamientoSerializer(tratamientos, many=True)
    registrar_log(request.user.id_usuario, "Tratamiento", "ver")
    return Response(serializer.data)


# Ver tratamiento por ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_tratamiento(request, id_tratamiento):
    try:
        tratamiento = Tratamiento.objects.get(id_tratamiento=id_tratamiento, estado=True)
    except Tratamiento.DoesNotExist:
        return Response({"error": "Tratamiento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = TratamientoSerializer(tratamiento)
    registrar_log(request.user.id_usuario, "Tratamiento", "ver")
    return Response(serializer.data)


# Crear tratamiento
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_tratamiento(request):
    data = request.data.copy()
    data["estado"] = True

    serializer = TratamientoSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        registrar_log(request.user.id_usuario, "Tratamiento", "crear")
        return Response({"mensaje": "Tratamiento creado correctamente."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Editar tratamiento
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def editar_tratamiento(request, id_tratamiento):
    try:
        tratamiento = Tratamiento.objects.get(id_tratamiento=id_tratamiento, estado=True)
    except Tratamiento.DoesNotExist:
        return Response({"error": "Tratamiento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = TratamientoSerializer(tratamiento, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        registrar_log(request.user.id_usuario, "Tratamiento", "editar")
        return Response({"mensaje": "Tratamiento actualizado correctamente."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Eliminar tratamiento (lógica)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_tratamiento(request, id_tratamiento):
    try:
        tratamiento = Tratamiento.objects.get(id_tratamiento=id_tratamiento, estado=True)
    except Tratamiento.DoesNotExist:
        return Response({"error": "Tratamiento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    tratamiento.estado = False
    tratamiento.save()
    registrar_log(request.user.id_usuario, "Tratamiento", "eliminar")
    return Response({"mensaje": "Tratamiento eliminado correctamente."})


from django.db.models import Q
#personal
# Listar personal activo
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_personal(request):
    id_usuario_log = request.query_params.get('id_usuario', None)
    personal = Usuario.objects.filter(Q(rol='veterinario') | Q(rol='recepcionista'), estado=True)
    serializer = ClienteSerializer(personal, many=True)
    return Response(serializer.data)


# Ver personal por ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_personal(request, id_personal):
    try:
        cliente = Usuario.objects.get(id_usuario=id_personal)
    except Usuario.DoesNotExist:
        return Response({"error": "Personal no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ClienteSerializer(cliente)
    registrar_log(request.user.id_usuario, "Personal", "ver", id_personal)
    return Response(serializer.data)


# Editar Personal
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def editar_personal(request, id_personal):
    try:
        cliente = Usuario.objects.get(id_usuario=id_personal)
    except Usuario.DoesNotExist:
        return Response({"error": "Personal no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ClienteSerializer(cliente, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        registrar_log(request.user.id_usuario, "Personal", "editar", id_personal)
        return Response({"mensaje": "Personal actualizado exitosamente."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Eliminar Personal (lógico)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_personal(request, id_personal):
    try:
        cliente = Usuario.objects.get(id_usuario=id_personal)
    except Usuario.DoesNotExist:
        return Response({"error": "Personal no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    cliente.estado = False
    cliente.save()
    registrar_log(request.user.id_usuario, "Personal", "eliminar", id_personal)
    return Response({"mensaje": "Personal eliminado correctamente."})

#crear personal
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_personal(request):
    data = request.data.copy()
    data['estado'] = True
    data['codigo'] = '-99'
    data['contrasenia_hash'] = make_password(data['ci'] + "VetLaUnion")

    serializer = ClienteSerializer(data=data)
    if serializer.is_valid():
        cliente = serializer.save()
        registrar_log(request.user.id_usuario, "Personal", "crear", cliente.id_usuario)
        return Response({"mensaje": "Personal creado exitosamente."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
