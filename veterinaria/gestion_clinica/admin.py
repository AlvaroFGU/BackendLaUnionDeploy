from django.contrib import admin

# Register your models here.
from .models import (
    Usuario, Mascota, Vacuna, MascotaVacuna, Cita, 
    ComposicionConsulta, ObservacionSintoma, EvaluacionDiagnostico,
    Tratamiento, AccionTratamiento, Receta, ChatbotConsulta, LogAcceso
)

# Registrar cada modelo en el panel de administración
admin.site.register(Usuario)
admin.site.register(Mascota)
admin.site.register(Vacuna)
admin.site.register(MascotaVacuna)
admin.site.register(Cita)
admin.site.register(ComposicionConsulta)
admin.site.register(ObservacionSintoma)
admin.site.register(EvaluacionDiagnostico)
admin.site.register(Tratamiento)
admin.site.register(AccionTratamiento)
admin.site.register(Receta)
admin.site.register(ChatbotConsulta)
admin.site.register(LogAcceso)