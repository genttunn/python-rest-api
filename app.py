from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from pandas import pandas as pd
from flask_cors import CORS
import pymysql
import dbparams
import os
import json

# Get current dir
current_dir = str(os.path.abspath(os.path.dirname(__file__)))
# Configs
app = Flask(__name__)
connection_string = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
    dbparams.mysql_user, dbparams.mysql_password, dbparams.mysql_host, dbparams.mysql_db)

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)
data = pd.read_csv("./csv/features_texture.csv")
# print(data.columns)
#########################################
# Classes


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    birthdate = db.Column(db.DateTime)
    gender = db.Column(db.String(2))
    studies = db.relationship('Study', backref='Study')
    labels = db.relationship('Label', backref='Label')

    def __init__(self, first_name, last_name, birthdate, gender):
        self.firstName = first_name
        self.lastName = last_name
        self.birthdate = birthdate
        self.gender = gender


StudyAlbum = db.Table('study_album',
                      db.Column('idStudy', db.Integer, db.ForeignKey(
                          'study.id'), primary_key=True),
                      db.Column('idAlbum', db.Integer, db.ForeignKey(
                          'album.id'), primary_key=True)
                      )


class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timeStamp = db.Column(db.DateTime)
    idPatient = db.Column(db.Integer, db.ForeignKey(
        'patient.id'))
    series = db.relationship('Series', backref='SeriesS')
    albums = db.relationship('Album', backref='Study_to_Album',
                             lazy='dynamic', secondary=StudyAlbum)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    timeStamp = db.Column(db.DateTime)
    qibs = db.relationship('QIB', backref='QIB')
    studies = db.relationship('Study', backref='Album_to_Study',
                              lazy='dynamic', secondary=StudyAlbum)


class Modality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    series = db.relationship('Series', backref='SeriesM')

    def __init__(self, name, description):
        self.name = name
        self.description = description


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timeStamp = db.Column(db.DateTime)
    idStudy = db.Column(db.Integer, db.ForeignKey(
        'study.id'))
    idModality = db.Column(db.Integer, db.ForeignKey(
        'modality.id'))
    images = db.relationship('Image', backref='Image')


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timeStamp = db.Column(db.DateTime)
    location = db.Column(db.Integer)
    thickness = db.Column(db.Integer)
    idSeries = db.Column(db.Integer, db.ForeignKey(
        'series.id'))


class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    idPatient = db.Column(db.Integer, db.ForeignKey(
        'patient.id'))

    def __init__(self, name, description):
        self.name = name
        self.description = description


class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    features = db.relationship('Feature', backref='Feature')


class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    idFamily = db.Column(db.Integer, db.ForeignKey(
        'family.id'))

    def __init__(self, name, id_family):
        self.name = name
        self.idFamily = id_family


class QIB(db.Model):
    __tablename__ = 'qib'
    id = db.Column(db.Integer, primary_key=True)
    timeStamp = db.Column(db.DateTime)
    idAlbum = db.Column(db.Integer, db.ForeignKey(
        'album.id'))

    def __init__(self, time_stamp, id_album):
        self.timeStamp = time_stamp
        self.idAlbum = id_album


class QIBFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idQIB = db.Column(db.Integer, db.ForeignKey('qib.id'))
    idFeature = db.Column(db.Integer, db.ForeignKey(
        'feature.id'))
    featureValue = db.Column(db.Float)

    def __init__(self, id_qib, id_feature, value):
        self.idQIB = id_qib
        self.idFeature = id_feature
        self.featureValue = value


class PatientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'firstName', 'lastName', 'birthdate', 'gender')


class FeatureSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'idFamily')


class AlbumSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'timeStamp')


class StudyAlbumSchema(ma.Schema):
    class Meta:
        fields = ('idStudy', 'idAlbum')


class QIBSchema(ma.Schema):
    class Meta:
        fields = ('id', 'timeStamp', 'idAlbum')


class QIBFeatureSchema(ma.Schema):
    class Meta:
        fields = ('idQIB', 'idFeature', 'featureValue')


patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)

feature_schema = FeatureSchema()
features_schema = FeatureSchema(many=True)

album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)

qib_schema = QIBSchema()
qibs_schema = QIBSchema(many=True)

qib_feature_schema = QIBFeatureSchema()
qib_features_schema = QIBFeatureSchema(many=True)

study_album_schema = StudyAlbumSchema()
study_albums_schema = StudyAlbumSchema(many=True)


#########################################
# Endpoints
@app.route('/', methods=['GET'])
def get():
    print('console got!')
    return jsonify({'test': current_dir})


@app.route('/insertPatient', methods=['POST'])
def insert_patient():
    data = request.json
    print(data["birthdate"])
    pa_search = Patient.query.filter_by(
        firstName=data["firstName"], lastName=data["lastName"], birthdate=data["birthdate"], gender=data["gender"]).first()
    if pa_search is None:
        pa = Patient(data["firstName"], data["lastName"],
                     data["birthdate"], data["gender"])
        db.session.add(pa)
        db.session.commit()
        db.session.refresh(pa)
    print(pa.id)
    all_patients = Patient.query.all()
    results = patients_schema.dump(all_patients)
    return jsonify(results)


@app.route('/qibs', methods=['GET'])
def get_qibs():
    all_qibs = QIB.query.all()
    results = qibs_schema.dump(all_qibs)
    return jsonify(results)


@app.route('/qibs/<album_id>', methods=['GET'])
def get_qibs_by_album(album_id):
    all_qibs = QIB.query.filter_by(idAlbum=album_id).all()
    results = qibs_schema.dump(all_qibs)
    return jsonify(results)


@app.route('/qib_features', methods=['GET'])
def get_qib_features():
    all_qib_features = QIBFeature.query.all()
    results = qib_features_schema.dump(all_qib_features)
    return jsonify(results)


@app.route('/qib_features/<qib_id>', methods=['GET'])
def get_qib_features_by_qib(qib_id):
    all_qib_features = QIBFeature.query.filter_by(idQIB=qib_id).all()
    results = qib_features_schema.dump(all_qib_features)
    return jsonify(results)


@app.route('/features', methods=['GET'])
def get_features():
    all_features = Feature.query.all()
    results = features_schema.dump(all_features)
    return jsonify(results)


@app.route('/albums', methods=['GET'])
def get_albums():
    all_albums = Album.query.all()
    results = albums_schema.dump(all_albums)
    return jsonify(results)

# get all albums belongingto study 1
@app.route('/albumtest', methods=['GET'])
def get_albums_test():
    all_albums = Album.query.filter(Album.studies.any(id=1)).all()
    results = albums_schema.dump(all_albums)
    return jsonify(results)

# get all albums belonging to study 1
@app.route('/uploadCSV', methods=['GET'])
def insert_feature():
    add_features(data)
    add_modalities(data)
    add_patients(data)
    qibID = add_qib()
    add_qib_features(data, qibID)
    all_features = Feature.query.all()
    results = features_schema.dump(all_features)
    return jsonify(results)


@app.route('/getPatLab', methods=['GET'])
def get_pat_lab():
    add_labels(data)


######################################
# helper funcs


def add_qib():
    qib = QIB(datetime.now(), 1)
    db.session.add(qib)
    db.session.commit()
    db.session.refresh(qib)
    return qib.id


def add_qib_features(data, qibID):
    for i in data.columns:
        feature_search = Feature.query.filter_by(name=i).first()
        if feature_search != None:
            print(feature_search.id)
            for a in data[i]:
                qf = QIBFeature(qibID, feature_search.id, a)
                db.session.add(qf)
                db.session.commit()


def add_features(data):
    for i in data.columns:
        feature_search = Feature.query.filter_by(name=i).first()
        if feature_search is None and i not in ['patientID', 'modality', 'label']:
            fe = Feature(i, 1)
            db.session.add(fe)
            db.session.commit()
            db.session.refresh(fe)


def add_modalities(data):
    for i in data["modality"]:
        modality_search = Modality.query.filter_by(name=i).first()
        if modality_search is None:
            mo = Modality(i, "To be updated")
            db.session.add(mo)
            db.session.commit()


def add_patients(data):
    for i in data["patientID"]:
        extracted_name = i[:i.index("_")].split(' ')
        first_name = extracted_name[0]
        last_name = extracted_name[1]
        pa_search = Patient.query.filter_by(
            firstName=first_name, lastName=last_name).first()
        if pa_search is None:
            pa = Patient(first_name, last_name, "2000-01-01", "F")
            db.session.add(pa)
            db.session.commit()


def add_labels(data):
    for i in (data["patientID"], data["modality"]):
        print(i[0])
        print(i[1])

    # label_search = Label.query.filter_by(name=i).first()
    # if label_search is None:
    #     lb = Label(i, "To be updated")
    #     db.session.add(lb)
    #     db.session.commit()
###################################################################


# Run server
if __name__ == '__main__':
    app.run(debug=True)


# class QIBFeatureSchema(ma.Schema):
#     class Meta:
#         fields = ('idQIB', 'idFeature', 'value')

# qib_feature_schema = QIBFeatureSchema()
# qib_features_schema = QIBFeatureSchema(many=True)

# Column('last_updated', DateTime, onupdate=datetime.datetime.now),
