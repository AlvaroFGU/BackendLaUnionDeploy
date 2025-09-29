from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Usuario, Mascota, Vacuna, MascotaVacuna, Cita, 
    ComposicionConsulta, ObservacionSintoma, EvaluacionDiagnostico,
    Tratamiento, AccionTratamiento, Receta, ChatbotConsulta, LogAcceso
)
from rest_framework.validators import UniqueValidator

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class MascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = '__all__'

class VacunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacuna
        fields = '__all__'

class MascotaVacunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MascotaVacuna
        fields = '__all__'

class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = '__all__'

class ComposicionConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComposicionConsulta
        fields = '__all__'

class ObservacionSintomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservacionSintoma
        fields = '__all__'

class EvaluacionDiagnosticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluacionDiagnostico
        fields = '__all__'

class TratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tratamiento
        fields = '__all__'

class AccionTratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccionTratamiento
        fields = '__all__'

class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = '__all__'

class ChatbotConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotConsulta
        fields = '__all__'

class LogAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogAcceso
        fields = '__all__'

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")

        # Validar contraseña con check_password
        if not user.check_password(password):
            raise serializers.ValidationError("Contraseña incorrecta")

        data = super().validate({"username": email, "password": password})

        data["user"] = {
            "id_usuario": user.id_usuario, 
            "nombre_completo": user.nombre_completo,
            "email": user.email,
            "rol": user.rol,
            "fotografia": user.fotografia,
        }
        return data


    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token
    

# validaciones de CRUD usurio cliente
    
class ClienteSerializer(serializers.ModelSerializer):
    ci = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Usuario.objects.all(),
                message="Este CI ya está registrado."
            )
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Usuario.objects.all(),
                message="Este correo ya está registrado."
            )
        ]
    )
    mascotas = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id_usuario', 'ci', 'telefono', 'nombre_completo', 'email', 'direccion', 'fotografia', 'rol', 'codigo', 'contrasenia_hash', 'mascotas']
    extra_kwargs = {
            'ci': {
                'error_messages': {
                    'unique': 'Este CI ya está registrado.'
                }
            },
            'email': {
                'error_messages': {
                    'unique': 'Este correo ya se encuentra registrado.'
                }
            }
        }
    def validate_ci(self, value):
        if len(value) > 12:
            raise serializers.ValidationError("El CI no puede tener más de 12 caracteres.")
        if len(value) < 6:
            raise serializers.ValidationError("El CI no puede tener menos de 6 caracteres.")
        if Usuario.objects.filter(ci=value).exclude(id_usuario=self.instance.id_usuario if self.instance else None).exists():
            raise serializers.ValidationError("Este CI ya está registrado.")
        return value

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exclude(id_usuario=self.instance.id_usuario if self.instance else None).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_telefono(self, value):
        if len(str(value)) != 8:
            raise serializers.ValidationError("El teléfono debe tener exactamente 8 dígitos.")
        if str(value)[0] not in ['2', '5', '6', '7']:
            raise serializers.ValidationError("El teléfono debe iniciar con 2, 5, 6 o 7.")
        return value

    def validate_nombre_completo(self, value):
        if not (5 <= len(value) <= 100):
            raise serializers.ValidationError("El nombre completo debe tener entre 5 y 100 caracteres.")
        return value

    def validate_direccion(self, value):
        if not (5 <= len(value) <= 255):
            raise serializers.ValidationError("La dirección debe tener entre 5 y 255 caracteres.")
        return value

    def get_mascotas(self, obj):
        return list(Mascota.objects.filter(propietario=obj, estado=True).values_list('nombre', flat=True))

#validaciones CRUD mascota
from datetime import date, timedelta

class MascotaSerializer(serializers.ModelSerializer):
    nombre_duenio = serializers.CharField(source='propietario.nombre_completo', read_only=True)
    ci_duenio = serializers.CharField(source='propietario.ci', read_only=True)

    class Meta:
        model = Mascota
        fields = '__all__'

    def validate_nombre(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre es obligatorio.")
        if len(value) > 50:
            raise serializers.ValidationError("Máximo 50 caracteres.")
        return value.strip()

    def validate_fecha_nacimiento(self, value):
        if value:
            hoy = date.today()
            hace_25_anios = hoy.replace(year=hoy.year - 25)

            if value > hoy:
                raise serializers.ValidationError("La fecha no puede ser mayor a la fecha actual.")
            if value < hace_25_anios:
                raise serializers.ValidationError("La fecha no puede ser menor a hace 25 años.")
        return value
    
class VacunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacuna
        fields = '__all__'
    
    def validate_nombre_vacuna(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("El nombre de la vacuna debe tener al menos 3 caracteres.")
        if len(value) > 100:
            raise serializers.ValidationError("El nombre de la vacuna no debe superar los 100 caracteres.")

        if Vacuna.objects.filter(nombre_vacuna__iexact=value).exclude(id_vacuna=self.instance.id_vacuna if self.instance else None).exists():
            raise serializers.ValidationError("Ya existe una vacuna con este nombre.")
        return value
    
    def validate_descripcion(self, value):
        if value:
            if len(value.strip()) < 10:
                raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres.")
            if len(value.strip()) > 250:
                raise serializers.ValidationError("La descripción no debe superar los 250 caracteres.")
        return value

    def validate_dosis_recomendada(self, value):
        if value and len(value.strip()) > 50:
            raise serializers.ValidationError("La dosis recomendada no debe superar los 50 caracteres.")
        return value

    def validate_edad_recomendada(self, value):
        if value and len(value.strip()) > 50:
            raise serializers.ValidationError("La edad recomendada no debe superar los 50 caracteres.")
        return value
    
class MascotaVacunaSerializer(serializers.ModelSerializer):
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)
    especie = serializers.CharField(source='mascota.especie', read_only=True)
    nombre_duenio = serializers.CharField(source='mascota.propietario.nombre_completo', read_only=True)
    nombre_veterinario = serializers.CharField(source='veterinario.nombre_completo', read_only=True)
    nombre_vacuna = serializers.CharField(source='vacuna.nombre_vacuna', read_only=True)
    descripcion_vacuna = serializers.CharField(source='vacuna.descripcion', read_only=True)

    class Meta:
        model = MascotaVacuna
        fields = '__all__'

    def validate(self, data):
        from datetime import date
        if data['fecha_aplicacion'] > date.today():
            raise serializers.ValidationError({"fecha_aplicacion": "La fecha de aplicación no puede ser futura."})
        return data


from django.utils import timezone

class CitaSerializer(serializers.ModelSerializer):
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)
    especie = serializers.CharField(source='mascota.especie', read_only=True)
    nombre_duenio = serializers.CharField(source='mascota.propietario.nombre_completo', read_only=True)
    nombre_veterinario = serializers.CharField(source='veterinario.nombre_completo', read_only=True)
    ci_veterinario = serializers.CharField(source='veterinario.ci', read_only=True)
    ci_duenio = serializers.CharField(source='mascota.propietario.ci', read_only=True)

    class Meta:
        model = Cita
        fields = '__all__'

    def validate_fecha_cita(self, value):
        # Verifica que la fecha no sea en el pasado
        if value < timezone.now():
            raise serializers.ValidationError("La fecha de la cita no puede tener una fecha pasada.")
        return value

    def validate_mascota(self, value):
        mascota = self.initial_data.get('mascota')  # Obtener la mascota desde los datos iniciales
        if mascota:
            # Verifica si la mascota ya tiene una cita programada o pendiente
            if Cita.objects.filter(mascota=mascota, estado_cita__in=['programada', 'pendiente']).exists():
                # Verifica si ya está programada
                if Cita.objects.filter(mascota=mascota, estado_cita='programada').exists():
                    raise serializers.ValidationError("La mascota ya tiene una cita programada.", code='mascota_programada')
                # Verifica si ya está pendiente
                elif Cita.objects.filter(mascota=mascota, estado_cita='pendiente').exists():
                    raise serializers.ValidationError("La mascota ya tiene una solicitud de cita pendiente.", code='mascota_pendiente')
        return value

    def validate_veterinario(self, value):
        veterinario = self.initial_data.get('veterinario')  # Obtener el veterinario desde los datos iniciales
        fecha_cita = self.initial_data.get('fecha_cita')  # Obtener la fecha de la cita desde los datos iniciales

        if veterinario and fecha_cita:
            # Verifica si el veterinario tiene una cita programada para el mismo horario
            if Cita.objects.filter(veterinario=veterinario, fecha_cita=fecha_cita).exists():
                raise serializers.ValidationError("El veterinario ya tiene una cita programada para este horario.", code='veterinario_ocupado')
        return value

    
class TratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tratamiento
        fields = '__all__'

    def validate_nombre_tratamiento(self, value):
        nombre = value.strip()
        tratamiento_id = self.instance.id_tratamiento if self.instance else None
        
        if Tratamiento.objects.filter(nombre_tratamiento__iexact=nombre)\
            .exclude(id_tratamiento=tratamiento_id).exists():
            raise serializers.ValidationError("El nombre del tratamiento ya existe.")
        
        return nombre

#consulta compleja
from django.db import transaction
from rest_framework import serializers
from .models import (
    ComposicionConsulta, ObservacionSintoma, EvaluacionDiagnostico,
    AccionTratamiento, Tratamiento, Receta
)

class ObservacionSintomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservacionSintoma
        fields = ['descripcion', 'proporcionado_por', 'severidad_aparente']

class EvaluacionDiagnosticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluacionDiagnostico
        fields = ['diagnostico', 'clasificacion_cie', 'notas']

class AccionTratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccionTratamiento
        fields = [
            'tratamiento', 'fecha_inicio', 'fecha_fin', 'observaciones',
            'monto_total', 'monto_cancelado'
        ]

    def validate(self, data):
        if data['monto_cancelado'] > data['monto_total']:
            raise serializers.ValidationError("El monto cancelado no puede ser mayor al monto total.")
        return data

class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = ['medicamento', 'dosis', 'fecha_emision', 'contenido']

class ComposicionConsultaSerializer(serializers.ModelSerializer):
    id_composicion = serializers.IntegerField(read_only=True)

    diagnostico = EvaluacionDiagnosticoSerializer(many=True, required=False, allow_null=True)
    observaciones = ObservacionSintomaSerializer(many=True, required=False, allow_null=True)
    tratamientos = AccionTratamientoSerializer(many=True, required=False, allow_null=True)
    recetas = RecetaSerializer(many=True, required=False, allow_null=True)
    vacunas = MascotaVacunaSerializer(many=True, required=False, allow_null=True)
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)
    nombre_duenio = serializers.CharField(source='mascota.propietario.nombre_completo', read_only=True)
    nombre_veterinario = serializers.CharField(source='veterinario.nombre_completo', read_only=True) 

    class Meta:
        model = ComposicionConsulta
        fields = [
            'id_composicion',
            'mascota', 'veterinario', 'fecha_consulta', 'motivo_consulta',
            'costo_consulta', 'monto_cancelado', 'peso', 'temperatura', 'estado',
            'diagnostico', 'observaciones', 'tratamientos', 'recetas', 'nombre_mascota', 'nombre_duenio', 'nombre_veterinario', 'vacunas'
        ]

    def _ensure_list(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @transaction.atomic
    def create(self, validated_data):
        diagnostico_data = self._ensure_list(validated_data.pop('diagnostico', []))
        observaciones_data = self._ensure_list(validated_data.pop('observaciones', []))
        tratamientos_data = self._ensure_list(validated_data.pop('tratamientos', []))
        recetas_data = self._ensure_list(validated_data.pop('recetas', []))

        composicion = ComposicionConsulta.objects.create(**validated_data)

        for d in diagnostico_data:
            EvaluacionDiagnostico.objects.create(composicion=composicion, **d)

        for o in observaciones_data:
            ObservacionSintoma.objects.create(composicion=composicion, **o)

        for t in tratamientos_data:
            AccionTratamiento.objects.create(composicion=composicion, **t)

        for r in recetas_data:
            Receta.objects.create(composicion=composicion, **r)

        return composicion
    

class ObservacionSintomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservacionSintoma
        fields = ['id_observacion', 'descripcion', 'proporcionado_por', 'severidad_aparente']

class EvaluacionDiagnosticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluacionDiagnostico
        fields = ['id_diagnostico', 'diagnostico', 'clasificacion_cie', 'notas']

class AccionTratamientoSerializer(serializers.ModelSerializer):
    tratamiento_nombre = serializers.CharField(source='tratamiento.nombre_tratamiento', read_only=True)
    nombre_mascota = serializers.CharField(source='composicion.mascota.nombre', required=False, allow_null=True)
    nombre_duenio = serializers.CharField(source='composicion.mascota.propietario.nombre_completo', required=False, allow_null=True)
    nombre_veterinario = serializers.CharField(source='composicion.veterinario.nombre_completo', required=False, allow_null=True)
    class Meta:
        model = AccionTratamiento
        fields = ['nombre_duenio', 'nombre_veterinario', 'id_accion', 'nombre_mascota', 'tratamiento', 'tratamiento_nombre', 'fecha_inicio', 'fecha_fin', 'observaciones', 'monto_total', 'monto_cancelado', 'estado_tratamiento']


class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = ['id_receta', 'fecha_emision', 'medicamento', 'dosis', 'contenido']

