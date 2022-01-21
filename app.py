import json
from builtins import float
from datetime import date, datetime
import mimetypes
from tokenize import Double

import urllib3
import urllib

from authlib.integrations.flask_client import OAuth
from threading import local
import pymongo
from werkzeug.exceptions import HTTPException

from clases import articulo, usuario
import requests as requests
from flask import Flask, request, jsonify, Response, render_template, session, redirect, url_for
from flask_pymongo import PyMongo
# from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util, ObjectId

import re
# from unicodedata import normalize

import cloudinary
import cloudinary.uploader
import geocoder

app = Flask(__name__)
app.config[
    'MONGO_URI'] = 'mongodb+srv://adrian:adrian@clusteringweb.i2g2k.mongodb.net/Examen3_Vendaval?retryWrites=true&w=majority'
mongo = PyMongo(app)

app.secret_key = 'sadffasfsadc xiyufevbsdasdvfssazd'

cloudinary.config(
    cloud_name="dwgwt0snv",
    api_key="594397889467117",
    api_secret="fne7WyjOh1G5wOBt5oA1L4aW6AU"
)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='426257895649-ge5if5bhhc1cr1lj0a83uumtjh8otjio.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)


def get_usuario_por_correo(correo):
    usuario = mongo.db.usuario.find_one({'correo': correo})
    return usuario


def crear_usuario_aux(nombre, apellidos, correo):
    id_usuario = -1

    if nombre and correo:
        id_usuario = mongo.db.usuario.insert_one(
            {
                "nombre": nombre,
                "apellidos": apellidos,
                "correo": correo,
            }
        ).inserted_id

    return id_usuario


def crear_articulo_aux(id_vendedor, descripcion, precio_salida, fotografia_c):
    if id_vendedor and descripcion and precio_salida and fotografia_c:
        id_articulo = mongo.db.articulo.insert_one(
            {
                "vendedor": ObjectId(id_vendedor),
                "descripcion": descripcion,
                "precio_salida": precio_salida,
                "imagenes": fotografia_c,
            }
        ).inserted_id
        response = {'creado': 3, 'mensaje': 'Articulo creado con éxito con ID = ' + str(id_articulo)}
    else:
        if id_vendedor is None:
            response = {'creado': 2, 'mensaje': 'No se ha añadido un artículo porque no existe vendedor.'}
        else:
            response = {'creado': 0,
                        'mensaje': 'No se ha podido crear un trayecto porque el campo coche, piloto, precio, ciudad destino, ciudad origen, direccion destino, direccion origen, fechaHora o plazas ofertadas  estan vacios'}
    return response


@app.route('/app/articulos/', methods=['POST'])
def crear_articulo_c():
    id_vendedor = ObjectId(session['id'])  # este id del usuario es el vendedor
    descripcion = request.form.get('descripcion')
    precio_salida = request.form.get('precio_salida')

    if id_vendedor and descripcion and precio_salida:
        fotografia_c = request.files['imagen']
        if fotografia_c:
            response = cloudinary.uploader.upload(fotografia_c)
            fotografia_c = response["url"]
        else:
            fotografia_c = ""
        insertado = crear_articulo_aux(id_vendedor, descripcion, precio_salida, fotografia_c)
        return redirect('/app/articulos/' + session['id'])
    else:
        return render_template('crear_articulo.html')

'''
@app.route('/app/articulos/<id_articulo>', methods=['GET'])
def get_articulo_c(id_articulo):
    if session.get("id"):
        if session.get("id_trayecto"):
            session.pop('id_trayecto')
        articulo_aux = articulo.get_full_trayecto(id_articulo)
        return render_template('visualizar_trayecto.html', trayecto=trayecto_aux, valoracion_media=valoracion_media,
                               n_valoraciones=n_valoraciones, fecha_actual=datetime.now())
    else:
        session["id_trayecto"] = id_trayecto
        return redirect(url_for('index2'))
'''

@app.route('/app', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/auth', methods=['GET'])
def login_oauth():
    token = google.authorize_access_token()

    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    correo = user_info["email"]

    user = get_usuario_por_correo(correo)
    if user:
        session['id'] = str(user['_id'])
    else:
        try:
            apellidos = user_info["family_name"]
        except:
            apellidos = ''

        id_u = crear_usuario_aux(user_info["given_name"], apellidos, correo)
        session['id'] = str(id_u)

    session['token'] = token

    return redirect('/app')


@app.route('/login')
def login_google():
    google = oauth.create_client('google')
    redirect_uri = url_for('login_oauth', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/')
def index2():
    return render_template("login.html")


@app.route('/app/logout')
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8080)
