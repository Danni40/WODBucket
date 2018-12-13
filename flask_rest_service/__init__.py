import os
from flask import Flask
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask import make_response
from bson.json_util import dumps
import requests

#MONGO_URL = os.environ.get('MONGO_URL')

#if not MONGO_URL:
    #MONGO_URL = 'mongodb://127.0.0.1:27017/test'

app = Flask(__name__, static_url_path = "", static_folder = "static")
app.config['DEBUG'] = True
app.config['STATIC_FOLDER'] = '/static'

#app.config['MONGO_URI'] = MONGO_URL
app.config['MONGO_DBNAME'] = 'wod_bucket'
app.config['MONGO_URI'] = 'mongodb://danni40:Tiagdtd39#(01@ds131954.mlab.com:31954/wod_bucket'
mongo = PyMongo(app)

def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp

DEFAULT_REPRESENTATIONS = {'application/json': output_json}
api = Api(app)
api.representations = DEFAULT_REPRESENTATIONS

#import the app
import flask_rest_service.main