from feature_manager import dbparams
from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = dbparams.connection_string

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)
from feature_manager import routes

