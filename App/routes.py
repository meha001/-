__author__ = 'meha001'

from App import app
from flask_restful import Api  # Исправленный импорт
from App.controller import Protected, Login

api = Api(app, default_mediatype="application/json")
api.add_resource(Login, '/login')
api.add_resource(Protected, '/protected')