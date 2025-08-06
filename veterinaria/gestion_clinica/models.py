from django.db import models

# ============================
# Usuarios
# ============================
class Usuario(models.Model):
    ROLES = [
        ('administrador', 'Administrador'),
        ('veterinario', 'Veterinario'),
        ('recepcionista', 'Recepcionista'),
        ('cliente', 'Cliente'),
    ]

    id_usuario = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contrasenia_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, choices=ROLES)
    fotografia = models.CharField(max_length=255, blank=True, null=True)
    codigo = models.CharField(max_length=6, blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return f"{self.nombre_completo} ({self.rol})"

# ============================
# Mascotas
# ============================
class Mascota(models.Model):
    SEXO = [
        ('M', 'Macho'),
        ('F', 'Hembra'),
    ]

    id_mascota = models.AutoField(primary_key=True)
    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=50)
    especie = models.CharField(max_length=50, blank=True, null=True)
    raza = models.CharField(max_length=50, blank=True, null=True)
    sexo = models.CharField(max_length=1, choices=SEXO, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    fotografia = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'mascota'

    def __str__(self):
        return f"{self.nombre} - {self.propietario.nombre_completo}"

# ============================
# Vacunas
# ============================
class Vacuna(models.Model):
    id_vacuna = models.AutoField(primary_key=True)
    nombre_vacuna = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    dosis_recomendada = models.CharField(max_length=50, blank=True, null=True)
    edad_recomendada = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'vacuna'

    def __str__(self):
        return self.nombre_vacuna


class MascotaVacuna(models.Model):
    id_mascota_vacuna = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    vacuna = models.ForeignKey(Vacuna, on_delete=models.CASCADE)
    fecha_aplicacion = models.DateField()
    lote_vacuna = models.CharField(max_length=50, blank=True, null=True)
    proxima_dosis = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'mascota_vacuna'
        unique_together = ('mascota', 'vacuna', 'fecha_aplicacion')

# ============================
# Citas
# ============================
class Cita(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('asistida', 'Asistida'),
        ('cancelada', 'Cancelada'),
    ]

    id_cita = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'veterinario'})
    fecha_cita = models.DateTimeField()
    estado_cita = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    motivo = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cita'

    def __str__(self):
        return f"Cita de {self.mascota.nombre} con {self.veterinario.nombre_completo}"

# ============================
# Historial clínico
# ============================
class ComposicionConsulta(models.Model):
    id_composicion = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'veterinario'})
    fecha_consulta = models.DateTimeField()
    motivo_consulta = models.TextField(blank=True, null=True)
    costo_consulta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monto_cancelado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'composicion_consulta'

    def __str__(self):
        return f"Consulta de {self.mascota.nombre} ({self.fecha_consulta.date()})"

class ObservacionSintoma(models.Model):
    id_observacion = models.AutoField(primary_key=True)
    PROPORCIONADO_POR = [
        ('cliente', 'Cliente'),
        ('chatbot', 'Chatbot'),
        ('veterinario', 'Veterinario'),
    ]

    composicion = models.ForeignKey(ComposicionConsulta, on_delete=models.CASCADE)
    descripcion = models.TextField()
    proporcionado_por = models.CharField(max_length=20, choices=PROPORCIONADO_POR)
    severidad_aparente = models.CharField(max_length=20, choices=[('leve', 'Leve'), ('moderado', 'Moderado'), ('grave', 'Grave')])

    class Meta:
        db_table = 'observacion_sintoma'

    def __str__(self):
        return f"Síntoma: {self.descripcion[:20]}..."

class EvaluacionDiagnostico(models.Model):
    id_diagnostico = models.AutoField(primary_key=True)
    composicion = models.ForeignKey(ComposicionConsulta, on_delete=models.CASCADE)
    diagnostico = models.TextField()
    clasificacion_cie = models.CharField(max_length=10, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'evaluacion_diagnostico'

# ============================
# Tratamientos
# ============================
class Tratamiento(models.Model):
    id_tratamiento = models.AutoField(primary_key=True)
    nombre_tratamiento = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    via_administracion = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'tratamiento'

    def __str__(self):
        return self.nombre_tratamiento

class AccionTratamiento(models.Model):
    id_accion = models.AutoField(primary_key=True)
    composicion = models.ForeignKey(ComposicionConsulta, on_delete=models.CASCADE)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monto_cancelado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'accion_tratamiento'

# ============================
# Recetas
# ============================
class Receta(models.Model):
    id_receta = models.AutoField(primary_key=True)
    composicion = models.ForeignKey(ComposicionConsulta, on_delete=models.CASCADE)
    fecha_emision = models.DateField()
    contenido = models.TextField()

    class Meta:
        db_table = 'receta'

# ============================
# Chatbot y logs
# ============================
class ChatbotConsulta(models.Model):
    id_chatbot = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    sintomas_ingresados = models.TextField()
    severidad_estimada = models.CharField(max_length=20, choices=[('no urgente', 'No Urgente'), ('moderado', 'Moderado'), ('crítico', 'Crítico')])
    respuesta = models.TextField()
    fecha = models.DateTimeField()

    class Meta:
        db_table = 'chatbot_consulta'

class LogAcceso(models.Model):
    ACCIONES = [
        ('ver', 'Ver'),
        ('editar', 'Editar'),
        ('crear', 'Crear'),
        ('eliminar', 'Eliminar'),
    ]
    id_log = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    modulo = models.CharField(max_length=50)
    fecha_acceso = models.DateTimeField()
    accion = models.CharField(max_length=50, choices=ACCIONES)

    class Meta:
        db_table = 'log_acceso'
