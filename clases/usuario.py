import app
from datetime import datetime
'''
def get_full_usuario(id_usuario):
    u = app.get_usuario_aux(id_usuario)
    valoracionMedia, nValoraciones = app.get_valoraciones_media_aux(id_usuario)

    usuario = {
        'id': u['_id'],
        'nombre': u['nombre'],
        'apellidos': u['apellidos'],
        'descripcion': u['descripcion'],
        'fotografia': u['fotografia'],
        'coches': u['listaCoches'],
        'valoraciones': get_valoraciones_usuario(u['listaValoracionesRecibidas']),
        'valoracionMedia': valoracionMedia,
        'numValoraciones': nValoraciones
    }
    return usuario


'''