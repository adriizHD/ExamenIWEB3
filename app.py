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

from clases import trayecto, usuario
import requests as requests
from flask import Flask, request, jsonify, Response, render_template, session, redirect, url_for
from flask_pymongo import PyMongo
# from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util, ObjectId

import re
#from unicodedata import normalize

import cloudinary
import cloudinary.uploader
import geocoder

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://adrian:adrian@clusteringweb.i2g2k.mongodb.net/iweb_llm?retryWrites=true&w=majority'
mongo = PyMongo(app)

app.secret_key = 'sadffasfsadc xiyufevbsdasdvfssazd'

cloudinary.config(
  cloud_name = "dwgwt0snv",
  api_key = "594397889467117",
  api_secret = "fne7WyjOh1G5wOBt5oA1L4aW6AU"
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
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)


def crear_usuario_aux(nombre, apellidos, correo, foto, des, admin):
    coches = []
    mensajes_env = []
    mensajes_rec = []
    valoraciones = []
    id_usuario = -1

    if nombre and correo and (admin or not admin):
        id_usuario = mongo.db.usuario.insert_one(
            {
                "nombre": nombre,
                "apellidos": apellidos,
                "correo": correo,
                "admin": admin,
                "descripcion": des,
                "fotografia": foto,
                "listaCoches": coches,
                "listaMensajesEnviados": mensajes_env,
                "listaMensajesRecibidos": mensajes_rec,
                "listaValoracionesRecibidas": valoraciones
            }
        ).inserted_id

    return id_usuario


def get_usuario_por_correo(correo):
    usuario = mongo.db.usuario.find_one({'correo': correo})
    return usuario


def get_valoraciones_recibidas_usuario_aux(id_usuario):
    usuario = mongo.db.usuario.find_one({'_id': ObjectId(id_usuario)})
    valoraciones = usuario['listaValoracionesRecibidas']
    return valoraciones


def get_valoraciones_media_aux(id_usuario):
    valoraciones = get_valoraciones_recibidas_usuario_aux(id_usuario)
    n_valoraciones = len(valoraciones)
    suma = 0.0
    for valoracion in valoraciones:
        suma += float(valoracion["puntuacion"])
    if suma != 0:
        return round(suma/n_valoraciones, 3), n_valoraciones
    else:
        return 0, n_valoraciones


def get_trayectos_fecha_cercana_a_lejana_aux():
    trayectos = mongo.db.trayecto.find({'fechaHora': {'$gt':datetime.now()}}).sort('fechaHora', pymongo.ASCENDING)
    return trayectos


def get_usuarios_contar_aux():
    cuenta = mongo.db.usuario.count_documents({})
    return cuenta


def get_trayectos_contar_aux():
    cuenta = mongo.db.trayecto.count_documents({})
    return cuenta


@app.route('/app/trayectos/<id_trayecto>', methods=['GET'])
def get_trayecto_c(id_trayecto):
    if session.get("id"):
        if session.get("id_trayecto"):
            session.pop('id_trayecto')
        trayecto_aux = trayecto.get_full_trayecto(id_trayecto)
        valoracion_media, n_valoraciones = get_valoraciones_media_aux(trayecto_aux["conductor"]["id"])
        print(session.get("id_trayecto"))
        return render_template('visualizar_trayecto.html', trayecto=trayecto_aux, valoracion_media=valoracion_media, n_valoraciones=n_valoraciones, fecha_actual=datetime.now())
    else:
        session["id_trayecto"] = id_trayecto
        return redirect(url_for('index2'))


@app.route('/app', methods=['GET'])
def index():
    doc_trayectos = get_trayectos_fecha_cercana_a_lejana_aux()
    list_trayectos = []
    for doc in doc_trayectos:
        list_trayectos.append(trayecto.get_lite_trayecto(doc['_id']))

    num_usuarios = get_usuarios_contar_aux()
    num_trayectos = get_trayectos_contar_aux()

    return render_template('index.html', trayectos=list_trayectos, numeroUsuarios=num_usuarios, numeroTrayectos=num_trayectos)


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
        session['admin'] = bool(user['admin'])
    else:
        try:
            apellidos = user_info["family_name"]
        except:
            apellidos = ''
        try:
            foto = user_info["picture"]
        except:
            foto = ''

        id_u = crear_usuario_aux(user_info["given_name"], apellidos, correo, foto, '', False)
        session['id'] = str(id_u)
        session['admin'] = False

    session['token'] = token
    if session.get("id_trayecto"):
        return redirect(url_for('get_trayecto_c', id_trayecto=session["id_trayecto"]))
    else:
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
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=8080)
