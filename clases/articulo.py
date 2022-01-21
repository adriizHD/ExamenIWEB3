import app

def get_full_articulo(id_articulo):
    articulo = app.get_trayecto_aux(id_articulo)

    articulo = {
        'id': articulo['_id'],
        'vendedor': articulo['vendedor'],
        'descripcion': articulo['descripcion'],
        'precio_salida': articulo['precio_salida'],
        'imagenes': articulo['imagenes'],
        'comprador': articulo['comprador']
    }
    return articulo
