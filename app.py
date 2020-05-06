from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from pandas import pandas as pd
from flask_cors import CORS
import pymysql
import dbparams
import models
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
# Schema
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


class QIBFeatureSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'idQIB', 'idFeature', 'featureValue', 'feature', 'qib')
    feature = ma.Nested(FeatureSchema)
    qib = ma.Nested(QIBSchema)

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
    print('Hello!')
    return jsonify({'test': current_dir})

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    try:
        if request.method == 'POST' and request.files:
            data = pd.read_csv(request.files['csv-file'])
            load_csv_to_db(data)
            return 'Upload ok'
    except Exception:
        return 'Upload failed'


@app.route('/qibs/', methods=['GET'])
def get_qibs():
    album = request.args.get('album', default = 0, type = int)
    date = request.args.get('date', default = '*', type = str)
    print(datetime.now())
    if(album!=0 and date=='*'):
        all_qibs = models.QIB.query.filter(models.QIB.idAlbum==album).all()
    elif(album==0 and date!='*'):
        all_qibs = models.QIB.query.filter(models.QIB.timeStamp>=datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')).all()
    else:
        all_qibs = models.QIB.query.all()
    results = qibs_schema.dump(all_qibs)
    return jsonify(results)


@app.route('/qib_features', methods=['GET'])
def get_qib_features():
    all_qib_features = models.QIBFeature.query.all()
    results = qib_features_schema.dump(all_qib_features)
    return jsonify(results)


@app.route('/qib_features/<qib_id>', methods=['GET'])
def get_qib_features_by_qib(qib_id):
    all_qib_features = models.QIBFeature.query.filter_by(idQIB=qib_id).all()
    df = convert_to_df(all_qib_features)
    jsonRes = df.to_json()
    # results = qib_features_schema.dump(all_qib_features)
    return jsonRes

def convert_to_df(qib_feature_set):
    current_feature_name = ''
    feature_dict = {}
    for qb in qib_feature_set:
        if(qb.feature.name != current_feature_name):
            current_feature_name = qb.feature.name
            feature_dict[current_feature_name] = []
        if current_feature_name in feature_dict:
            feature_dict[current_feature_name].append(qb.featureValue)
    df = pd.DataFrame(data=feature_dict)
    return df

@app.route('/generate_feature_set/<qib_id>', methods=['POST'])
def generate_csv(qib_id):
    data = request.json
    feature_list = data["feature_list"] 
    feature_dict = {}
    all_qib_features = models.QIBFeature.query.filter_by(idQIB=qib_id).all()
    current_feature_name = ''
    for qb in all_qib_features:
        if(qb.feature.name != current_feature_name):
            current_feature_name = qb.feature.name
            if current_feature_name in feature_list:
                feature_dict[current_feature_name] = []
        if current_feature_name in feature_dict:
            feature_dict[current_feature_name].append(qb.featureValue)
    df = pd.DataFrame(data=feature_dict)
    file=current_dir + f"\\data\\{str(datetime.now().timestamp())}.csv"
    df.to_csv(file, index=False)
    return file




@app.route('/albums', methods=['GET'])
def get_albums():
    all_albums = models.Album.query.all()
    results = albums_schema.dump(all_albums)
    return jsonify(results)




@app.route('/test', methods=['GET'])
def get_qib_features_testy():
    all_qib_features = models.QIBFeature.query.all()
    results = qib_features_schema.dump(all_qib_features)
    return jsonify(results)


######################################
# helper funcs
def load_csv_to_db(data):
    try:
        add_features(data)
        add_modalities(data)
        add_patients(data)
        add_labels(data)
        qibID = add_qib()
        add_qib_features(data, qibID)
        return True
    except Exception:
        return False


def add_qib():
    qib = models.QIB(datetime.now(), 1)
    db.session.add(qib)
    db.session.commit()
    db.session.refresh(qib)
    return qib.id


def add_qib_features(data, qibID):
    for i in data.columns:
        feature_search = models.Feature.query.filter_by(name=i).first()
        if feature_search != None:
            print(feature_search.id)
            for a in data[i]:
                qf = models.QIBFeature(qibID, feature_search.id, a)
                db.session.add(qf)
                db.session.commit()


def add_features(data):
    for i in data.columns:
        feature_search = models.Feature.query.filter_by(name=i).first()
        if feature_search is None and i not in ['patientID', 'modality', 'label']:
            fe = models.Feature(i, 1)
            db.session.add(fe)
            db.session.commit()
            db.session.refresh(fe)


def add_modalities(data):
    for i in data["modality"]:
        modality_search = models.Modality.query.filter_by(name=i).first()
        if modality_search is None:
            mo = models.Modality(i, "To be updated")
            db.session.add(mo)
            db.session.commit()


def add_patients(data):
    for i in data["patientID"]:
        extracted_name = i[:i.index("_")].split(' ')
        first_name = extracted_name[0]
        last_name = extracted_name[1]
        pa_search = models.Patient.query.filter_by(
            firstName=first_name, lastName=last_name).first()
        if pa_search is None:
            pa = models.Patient(first_name, last_name, "2000-01-01", "F")
            db.session.add(pa)
            db.session.commit()


def add_labels(data):
    for index, row in data.iterrows():
        extracted_name = row.patientID[:row.patientID.index("_")].split(' ')
        first_name = extracted_name[0]
        last_name = extracted_name[1]
        pa_search = models.Patient.query.filter_by(
            firstName=first_name, lastName=last_name).first()
        if pa_search != None:
            label_search = models.Label.query.filter_by(
                idPatient=pa_search.id).first()
            if label_search is None:
                lb = models.Label(row.label, "To be updated")
                lb.idPatient = pa_search.id
                db.session.add(lb)
                db.session.commit()


###################################################################
# Run server
if __name__ == '__main__':
    app.run(debug=True)








# @app.route('/features', methods=['GET'])
# def get_features():
#     all_features = models.Feature.query.all()
#     results = features_schema.dump(all_features)
#     return jsonify(results)


# @app.route('/albums', methods=['GET'])
# def get_albums():
#     all_albums = models.Album.query.all()
#     results = albums_schema.dump(all_albums)
#     return jsonify(results)

# # get all albums belongingto study 1
# @app.route('/albumtest', methods=['GET'])
# def get_albums_test():
#     all_albums = models.Album.query.filter(models.Album.studies.any(id=1)).all()
#     results = albums_schema.dump(all_albums)
#     return jsonify(results)

# @app.route('/insertPatient', methods=['POST'])
# def insert_patient():
#     data = request.json
#     print(data["birthdate"])
#     pa_search = models.Patient.query.filter_by(
#         firstName=data["firstName"], lastName=data["lastName"], birthdate=data["birthdate"], gender=data["gender"]).first()
#     if pa_search is None:
#         pa = models.Patient(data["firstName"], data["lastName"],
#                      data["birthdate"], data["gender"])
#         db.session.add(pa)
#         db.session.commit()
#         db.session.refresh(pa)
#     print(pa.id)
#     all_patients = models.Patient.query.all()
#     results = patients_schema.dump(all_patients)
#     return jsonify(results)
