from rest_framework import serializers
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
