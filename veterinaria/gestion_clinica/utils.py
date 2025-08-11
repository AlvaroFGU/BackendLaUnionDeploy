# veterinaria/gestion_clinica/utils.py
from .models import LogAcceso
from django.utils import timezone

def registrar_log(usuario_id, modulo, accion, id_modulo):
    LogAcceso.objects.create(
        usuario_id=usuario_id,
        modulo=modulo,
        fecha_acceso=timezone.now(),
        accion=accion,
        codigo_modulo = id_modulo
    )
