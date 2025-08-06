from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Usuario, Mascota, Vacuna, MascotaVacuna, Cita, 
    ComposicionConsulta, ObservacionSintoma, EvaluacionDiagnostico,
    Tratamiento, AccionTratamiento, Receta, ChatbotConsulta, LogAcceso
)

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

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")

        if user.contraseña_hash != password:
            raise serializers.ValidationError("Contraseña incorrecta")

        data = super().validate({"username": email, "password": password})
        data["user"] = {
            "id": user.id,
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