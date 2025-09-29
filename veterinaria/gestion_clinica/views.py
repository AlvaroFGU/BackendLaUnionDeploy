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
                'refresh': str(refresh),
                'codigo': usuario.codigo,
                'ci': usuario.ci
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
        asunto = 'Código de recuperación de contraseña'
        mensaje = f'Hola {cliente.nombre_completo},\n\nTu contraseña es: {data['ci'] + "VetLaUnion"}'
        remitente = None  
        #destinatarios = [cliente.email]
        destinatarios = ["alvarofredgonza18@gmail.com"]

        send_mail(asunto, mensaje, remitente, destinatarios)
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_mascota_vacuna(request):
    serializer = MascotaVacunaSerializer(data=request.data)
    
    if serializer.is_valid():
        mascota = serializer.validated_data['mascota']
        veterinario = serializer.validated_data['veterinario']
        
        consulta_data = {
            'mascota': mascota.id_mascota,
            'veterinario': veterinario.id_usuario,
            'fecha_consulta': request.data.get('fecha_aplicacion'),  
            'motivo_consulta': 'Aplicación de vacuna',
            'costo_consulta': 0.00, 
            'monto_cancelado': 0.00,  
            'peso': 0.00, 
            'temperatura': 0.00,  
            'estado': True  
        }

        consulta_serializer = ComposicionConsultaSerializer(data=consulta_data)

        if consulta_serializer.is_valid():
            consulta = consulta_serializer.save() 

            serializer.validated_data['composicion'] = consulta.id_composicion
            serializer.save()
            return Response({"mensaje": "Vacuna registrada para la mascota correctamente."}, status=status.HTTP_201_CREATED)
        else:
            return Response(consulta_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


# Listar tratamientos activos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_tratamientos(request):
    tratamientos = Tratamiento.objects.filter(estado=True)
    serializer = TratamientoSerializer(tratamientos, many=True)
    return Response(serializer.data)


# Ver tratamiento por ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_tratamiento(request, id_tratamiento):
    try:
        tratamiento = Tratamiento.objects.get(id_tratamiento=id_tratamiento)
    except Tratamiento.DoesNotExist:
        return Response({"error": "Tratamiento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = TratamientoSerializer(tratamiento)
    registrar_log(request.user.id_usuario, "Tratamiento", "ver", id_tratamiento)
    return Response(serializer.data)


# Crear tratamiento
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_tratamiento(request):
    data = request.data.copy()
    data["estado"] = True

    serializer = TratamientoSerializer(data=data)
    if serializer.is_valid():
        tratamiento = serializer.save()
        registrar_log(request.user.id_usuario, "Tratamiento", "crear", tratamiento.id_tratamiento)
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
        registrar_log(request.user.id_usuario, "Tratamiento", "editar", id_tratamiento)
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
    registrar_log(request.user.id_usuario, "Tratamiento", "eliminar", id_tratamiento)
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


# Veterinarios activos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_veterinarios(request):
    veterinarios = Usuario.objects.filter(rol="veterinario", estado=True)
    data = [{"id_usuario": v.id_usuario, "nombre_completo": v.nombre_completo, "ci": v.ci} for v in veterinarios]
    return Response(data)


from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, time
from .serializers import CitaSerializer, MascotaSerializer

from datetime import datetime, time, timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_horarios_libres(request):
    fecha = request.query_params.get("fecha")
    if not fecha:
        return Response({"error": "Debe enviar una fecha"}, status=400)

    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    dia_semana = fecha_dt.weekday()  # 0 = lunes ... 6 = domingo

    # reglas de horario
    if dia_semana == 6:
        return Response([])  # domingo no disponible
    elif dia_semana == 5:
        hora_inicio, hora_fin = time(10, 0), time(13, 0)
    else:
        hora_inicio, hora_fin = time(10, 0), time(19, 0)

    horarios = []
    actual = datetime.combine(fecha_dt, hora_inicio)

    while actual.time() < hora_fin:
        count = Cita.objects.filter(
            fecha_cita__date=fecha_dt,
            fecha_cita__time=actual.time(),
            estado=True,
            estado_cita__in=["pendiente", "programada"]
        ).count()
        ocupado = count >= 2 
        if not ocupado:
            horarios.append(actual.strftime("%H:%M"))
        actual += timedelta(minutes=30)

    return Response(horarios)


# CRUD de citas
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_citas(request):
    hoy = timezone.now().date()
    
    Cita.objects.filter(
        estado=True,
        fecha_cita__date__lt=hoy,
        estado_cita='pendiente'
    ).update(estado_cita='cancelada')
    
    Cita.objects.filter(
        estado=True,
        fecha_cita__date__lt=hoy,
        estado_cita='programada'
    ).update(estado_cita='no asistida')
    
    citas = Cita.objects.filter(estado=True).select_related("mascota", "mascota__propietario", "veterinario")
    
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_cita(request):
    serializer = CitaSerializer(data=request.data)
    if serializer.is_valid():
        cita = serializer.save()
        registrar_log(request.user.id_usuario, "Cita", "crear", cita.id_cita)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancelar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk, estado=True)
    cita.estado_cita = "cancelada"
    cita.motivo = request.data.get("motivo", "")
    cita.save()
    return Response({"message": "Cita cancelada"})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def programar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk, estado=True)
    cita.estado_cita = "programada"
    if "veterinario" in request.data:
        cita.veterinario_id = request.data["veterinario"]
    cita.save()
    return Response({"message": "Cita programada"})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def asistir_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk, estado=True)
    cita.estado_cita = "asistida"
    cita.save()
    return Response({"message": "Cita marcada como asistida"})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def eliminar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    cita.estado = False
    cita.save()
    return Response({"message": "Cita eliminada"})


#crear consulta compleja
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_consulta(request):
    serializer = ComposicionConsultaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Consulta creada correctamente"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#lista consultas compleja
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_consultas(request):
    try:
        consultas = ComposicionConsulta.objects.filter(estado=True)
        serializer = ComposicionConsultaSerializer(consultas, many=True)
        data = serializer.data

        for c in data:
            cid = c['id_composicion']

            obs_qs = ObservacionSintoma.objects.filter(composicion_id=cid)
            c['observaciones'] = ObservacionSintomaSerializer(obs_qs, many=True).data

            diag_qs = EvaluacionDiagnostico.objects.filter(composicion_id=cid)
            c['diagnostico'] = EvaluacionDiagnosticoSerializer(diag_qs, many=True).data

            trt_qs = AccionTratamiento.objects.filter(composicion_id=cid)
            c['tratamientos'] = AccionTratamientoSerializer(trt_qs, many=True).data

            rec_qs = Receta.objects.filter(composicion_id=cid)
            c['recetas'] = RecetaSerializer(rec_qs, many=True).data

        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    # Consultas por ID de mascota
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_consultas_por_mascota(request, id_mascota):
    try:
        consultas = ComposicionConsulta.objects.filter(estado=True, mascota_id=id_mascota)
        consulta_serializer = ComposicionConsultaSerializer(consultas, many=True)

        for consulta in consulta_serializer.data:
            consulta_id = consulta['id_composicion']

            consulta['observaciones'] = ObservacionSintomaSerializer(
                ObservacionSintoma.objects.filter(composicion_id=consulta_id), many=True
            ).data

            consulta['diagnostico'] = EvaluacionDiagnosticoSerializer(
                EvaluacionDiagnostico.objects.filter(composicion_id=consulta_id), many=True
            ).data

            consulta['tratamientos'] = AccionTratamientoSerializer(
                AccionTratamiento.objects.filter(composicion_id=consulta_id), many=True
            ).data

            consulta['recetas'] = RecetaSerializer(
                Receta.objects.filter(composicion_id=consulta_id), many=True
            ).data

            consulta['vacunas'] = MascotaVacunaSerializer(
                MascotaVacuna.objects.filter(composicion=consulta_id), many=True
            ).data

        return Response(consulta_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Consultas por ID de veterinario
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_consultas_por_veterinario(request, id_veterinario):
    try:
        consultas = ComposicionConsulta.objects.filter(estado=True, veterinario_id=id_veterinario)
        consulta_serializer = ComposicionConsultaSerializer(consultas, many=True)

        for consulta in consulta_serializer.data:
            consulta_id = consulta['id_composicion']

            consulta['observaciones'] = ObservacionSintomaSerializer(
                ObservacionSintoma.objects.filter(composicion_id=consulta_id), many=True
            ).data

            consulta['diagnostico'] = EvaluacionDiagnosticoSerializer(
                EvaluacionDiagnostico.objects.filter(composicion_id=consulta_id), many=True
            ).data

            consulta['tratamientos'] = AccionTratamientoSerializer(
                AccionTratamiento.objects.filter(composicion_id=consulta_id), many=True
            ).data

            consulta['recetas'] = RecetaSerializer(
                Receta.objects.filter(composicion_id=consulta_id), many=True
            ).data

        return Response(consulta_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Consulta por ID de composición (consulta específica)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_consulta_por_id(request, id_composicion):
    try:
        consulta = ComposicionConsulta.objects.filter(estado=True, id_composicion=id_composicion).first()
        if not consulta:
            return Response({"mensaje": "Consulta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        consulta_serializer = ComposicionConsultaSerializer(consulta)

        consulta_data = consulta_serializer.data
        consulta_id = consulta_data['id_composicion']

        consulta_data['observaciones'] = ObservacionSintomaSerializer(
            ObservacionSintoma.objects.filter(composicion_id=consulta_id), many=True
        ).data

        consulta_data['diagnostico'] = EvaluacionDiagnosticoSerializer(
            EvaluacionDiagnostico.objects.filter(composicion_id=consulta_id), many=True
        ).data

        consulta_data['tratamientos'] = AccionTratamientoSerializer(
            AccionTratamiento.objects.filter(composicion_id=consulta_id), many=True
        ).data

        consulta_data['recetas'] = RecetaSerializer(
            Receta.objects.filter(composicion_id=consulta_id), many=True
        ).data

        return Response(consulta_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
# Listar accion_tratamientos activos
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_accion_tratamientos(request):
    accion_tratamientos = AccionTratamiento.objects.filter(estado=True)
    serializer = AccionTratamientoSerializer(accion_tratamientos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_especies(request):
    especies = Mascota.objects.filter(estado=True).values_list('especie', flat=True).distinct()

    return Response(especies)

# views_tratamientos.py  (puedes ponerlo en tu views.py si prefieres)
from decimal import Decimal, InvalidOperation

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import AccionTratamiento
from .serializers import AccionTratamientoSerializer


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def actualizar_pago_tratamiento(request, id_tratamiento: int):
    try:
        tratamiento = AccionTratamiento.objects.select_for_update().get(pk=id_tratamiento)
    except AccionTratamiento.DoesNotExist:
        return Response({"detail": "Tratamiento no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    monto_raw = request.data.get("monto_a_sumar", None)
    if monto_raw is None:
        return Response({"monto_a_sumar": ["Este campo es obligatorio."]}, status=status.HTTP_400_BAD_REQUEST)

    try:
        monto = Decimal(str(monto_raw))
    except (InvalidOperation, TypeError, ValueError):
        return Response({"monto_a_sumar": ["Debe ser un número válido."]}, status=status.HTTP_400_BAD_REQUEST)

    if monto < 0:
        return Response({"monto_a_sumar": ["No puede ser negativo."]}, status=status.HTTP_400_BAD_REQUEST)

    total = tratamiento.monto_total or Decimal("0")
    cancelado = tratamiento.monto_cancelado or Decimal("0")
    saldo = total - cancelado
    if monto > saldo:
        return Response(
            {"monto_a_sumar": [f"El monto no puede ser mayor al saldo ({saldo})."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tratamiento.monto_cancelado = cancelado + monto
    tratamiento.save(update_fields=["monto_cancelado"])

    return Response(AccionTratamientoSerializer(tratamiento).data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def actualizar_estado_tratamiento(request, id_tratamiento: int):
    try:
        tratamiento = AccionTratamiento.objects.get(pk=id_tratamiento)
    except AccionTratamiento.DoesNotExist:
        return Response({"detail": "Tratamiento no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    nuevo_estado = (request.data.get("estado_tratamiento") or "").strip().lower()
    validos = {"en curso", "completado", "cancelado"}
    if nuevo_estado not in validos:
        return Response(
            {"estado_tratamiento": [f"Estado inválido. Válidos: {', '.join(sorted(validos))}."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tratamiento.estado_tratamiento = nuevo_estado
    tratamiento.save(update_fields=["estado_tratamiento"])

    return Response(AccionTratamientoSerializer(tratamiento).data, status=status.HTTP_200_OK)


#exportar historial
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_datos_historial(request, id_mascota):
    try:
        mascota = Mascota.objects.get(pk=id_mascota)
        
        propietario = mascota.propietario
        
        # Obtener las consultas relacionadas con la mascota
        consultas = ComposicionConsulta.objects.filter(mascota=mascota)
        
        vacunas = MascotaVacuna.objects.filter(mascota=mascota)
        
        # Formato de la respuesta
        response_data = {
            "context": {
                "owner": {
                    "owner_name": propietario.nombre_completo,
                    "owner_address": propietario.direccion or "No disponible",
                    "owner_phone": str(propietario.telefono) if propietario.telefono else "No disponible",
                    "owner_email": propietario.email,
                    "owner_id": str(propietario.ci),
                },
                "pet": {
                    "pet_name": mascota.nombre,
                    "species": mascota.especie,
                    "breed": mascota.raza,
                    "date_of_birth": mascota.fecha_nacimiento.strftime("%Y-%m-%d"),
                    "sex": "Macho" if mascota.sexo == 'M' else "Hembra",
                }
            },
            "clinical_data": []
        }
        
        # Recopilación de datos clínicos
        for consulta in consultas:
            data = {
                "weight": f"{consulta.peso}kg",
                "temperature": f"{consulta.temperatura}°C",
                "symptoms": [],
                "diagnosis": [],
                "treatments": [],
                "vaccines": []
            }

            # Obtener observaciones
            observaciones = ObservacionSintoma.objects.filter(composicion=consulta)
            for obs in observaciones:
                data["symptoms"].append({
                    "symptom": obs.descripcion,
                    "severity": obs.severidad_aparente,
                })
            
            # Obtener diagnóstico
            diagnosticos = consulta.evaluaciondiagnostico_set.all()
            for diag in diagnosticos:
                data["diagnosis"].append({
                    "description": diag.diagnostico,
                    "code": diag.clasificacion_cie,
                })
            
            # Obtener tratamientos
            tratamientos = AccionTratamiento.objects.filter(composicion=consulta)
            for tratamiento in tratamientos:
                data["treatments"].append({
                    "name": tratamiento.tratamiento.nombre_tratamiento,
                    "dosage": tratamiento.observaciones,
                    "route": tratamiento.tratamiento.via_administracion or "No especificado",
                    "date_start": tratamiento.fecha_inicio.strftime("%Y-%m-%d"),
                    "date_finish": tratamiento.fecha_fin.strftime("%Y-%m-%d"),
                })
            
            # Obtener vacunas (Vacunas aplicadas en consulta)
            vacunas_aplicadas = MascotaVacuna.objects.filter(composicion=consulta.id_composicion)
            for vacuna in vacunas_aplicadas:
                data["vaccines"].append({
                    "vaccine_name": vacuna.vacuna.nombre_vacuna,
                    "date_administered": vacuna.fecha_aplicacion.strftime("%Y-%m-%d"),
                    "next_due": vacuna.proxima_dosis.strftime("%Y-%m-%d") if vacuna.proxima_dosis else "No disponible"
                })
            
            response_data["clinical_data"].append(data)
        
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#importarhistorial
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def importar_historial(request):
    try:
        data = request.data
        
        # Validar estructura básica
        if not data.get('context') or not data.get('clinical_data'):
            return Response({"mensaje": "Estructura de datos inválida"}, status=status.HTTP_400_BAD_REQUEST)
        
        context = data['context']
        clinical_data = data['clinical_data']
        
        with transaction.atomic():
            # 1. Crear o obtener propietario
            owner_data = context.get('owner', {})
            
            # Preparar datos para el serializer
            cliente_data = {
                'ci': owner_data.get('owner_id', ''),
                'nombre_completo': owner_data.get('owner_name', ''),
                'direccion': owner_data.get('owner_address', ''),
                'telefono': owner_data.get('owner_phone', ''),
                'email': owner_data.get('owner_email', ''),
                'rol': 'cliente',
                'codigo': '-99',
                'contrasenia_hash': 'vetImportData'
            }
            
            # Verificar si el cliente ya existe
            try:
                propietario = Usuario.objects.get(ci=cliente_data['ci'])
                # Si existe, actualizar los datos si es necesario
                serializer = ClienteSerializer(propietario, data=cliente_data, partial=True)
            except Usuario.DoesNotExist:
                # Si no existe, crear nuevo cliente
                serializer = ClienteSerializer(data=cliente_data)
            
            if serializer.is_valid():
                propietario = serializer.save()
            else:
                return Response({
                    "mensaje": "Error en datos del propietario",
                    "errores": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. Crear o obtener mascota
            pet_data = context.get('pet', {})
            mascota, created = Mascota.objects.get_or_create(
                nombre=pet_data.get('pet_name'),
                propietario=propietario,
                defaults={
                    'especie': pet_data.get('species', ''),
                    'raza': pet_data.get('breed', ''),
                    'fecha_nacimiento': parse_date(pet_data.get('date_of_birth')),
                    'sexo': 'M' if pet_data.get('sex') == 'Macho' else 'H',
                }
            )
            
            consultas_importadas = 0
            
            # 3. Procesar cada consulta clínica
            for consulta_data in clinical_data:
                try:
                    # Crear composición de consulta
                    composicion = ComposicionConsulta.objects.create(
                        mascota=mascota,
                        peso=extract_number(consulta_data.get('weight', '0')),
                        temperatura=extract_number(consulta_data.get('temperature', '0')),
                        fecha_consulta=timezone.now().date(),  # O usar fecha del archivo si está disponible
                    )
                    
                    # # 4. Procesar síntomas/observaciones
                    # for symptom in consulta_data.get('symptoms', []):
                    #     ObservacionSintoma.objects.create(
                    #         composicion=composicion,
                    #         descripcion=symptom.get('symptom', ''),
                    #         severidad_aparente=symptom.get('severity', 'leve'),
                    #     )
                    
                    # # 5. Procesar diagnósticos
                    # for diagnosis in consulta_data.get('diagnosis', []):
                    #     EvaluacionDiagnostico.objects.create(
                    #         composicion=composicion,
                    #         diagnostico=diagnosis.get('description', ''),
                    #         clasificacion_cie=diagnosis.get('code', ''),
                    #     )
                    
                    # # 6. Procesar tratamientos
                    # for treatment in consulta_data.get('treatments', []):
                    #     # Crear o obtener tratamiento base
                    #     tratamiento_base, created = Tratamiento.objects.get_or_create(
                    #         nombre_tratamiento=treatment.get('name', 'Tratamiento'),
                    #         defaults={
                    #             'via_administracion': treatment.get('route', 'No especificado'),
                    #             'user': request.user
                    #         }
                    #     )
                        
                    #     AccionTratamiento.objects.create(
                    #         composicion=composicion,
                    #         tratamiento=tratamiento_base,
                    #         observaciones=treatment.get('dosage', ''),
                    #         fecha_inicio=parse_date(treatment.get('date_start')),
                    #         fecha_fin=parse_date(treatment.get('date_finish')),
                    #         user=request.user
                    #     )
                    
                    # # 7. Procesar vacunas
                    # for vaccine in consulta_data.get('vaccines', []):
                    #     # Crear o obtener vacuna base
                    #     vacuna_base, created = Vacuna.objects.get_or_create(
                    #         nombre_vacuna=vaccine.get('vaccine_name', 'Vacuna'),
                    #         defaults={'user': request.user}
                    #     )
                        
                    #     MascotaVacuna.objects.create(
                    #         mascota=mascota,
                    #         vacuna=vacuna_base,
                    #         composicion=composicion,
                    #         fecha_aplicacion=parse_date(vaccine.get('date_administered')),
                    #         proxima_dosis=parse_date(vaccine.get('next_due')),
                    #         user=request.user
                    #     )
                    
                    # consultas_importadas += 1
                    
                except Exception as e:
                    # Continuar con la siguiente consulta si hay error en una
                    print(f"Error procesando consulta: {str(e)}")
                    continue
            
            return Response({
                "mensaje": "Importación completada",
                "consultas_importadas": consultas_importadas,
                "mascota_id": mascota.id_mascota,
                "propietario_id": propietario.id_usuario
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({"mensaje": f"Error en la importación: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def parse_date(date_string):
    """Convierte string de fecha a objeto date"""
    if not date_string or date_string == "No disponible":
        return None
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except:
        return None

def extract_number(text):
    """Extrae número de texto como '75kg' -> 75.0"""
    if not text:
        return 0.0
    try:
        import re
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        return float(numbers[0]) if numbers else 0.0
    except:
        return 0.0