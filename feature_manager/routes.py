from feature_manager import app, jsonify,request
from feature_manager.models import *
from feature_manager.schemas import *
from pandas import pandas as pd
import json

family_schema = FamilySchema()
families_schema = FamilySchema(many=True)
feature_schema = FeatureSchema()
features_schema = FeatureSchema(many=True)
qib_feature_schema = QIBFeatureSchema()
qib_features_schema = QIBFeatureSchema(many=True)
qib_schema = QIBSchema()
qibs_schema = QIBSchema(many=True)
study_schema = StudySchema()
studies_schema = StudySchema(many=True)
album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)
study_album_schema = StudyAlbumSchema()
study_albums_schema = StudyAlbumSchema(many=True)

data = pd.read_csv("./csv/features_intensity.csv")

@app.route("/", methods=['GET'])
def hey():
    return 'hey new'

@app.route("/test", methods=['GET'])
def test():
    all_families = Family.query.all()
    results = families_schema.dump(all_families)
    return jsonify(results)

@app.route("/test_features", methods=['GET'])
def test_features():
    all_features = Feature.query.all()
    results = features_schema.dump(all_features)
    return jsonify(results)

@app.route('/qib_features/<qib_id>', methods=['GET'])
def get_qib_features_by_qib(qib_id):
    all_qib_features = QIBFeature.query.filter_by(idQIB=qib_id).all()
    results = qib_features_schema.dump(all_qib_features)
    return jsonify(results)


@app.route('/qibs/', methods=['GET'])
def get_qibs():
    album = request.args.get('album', default = 0, type = int)
    date = request.args.get('date', default = '*', type = str)
    if(album!=0 and date=='*'):
        all_qibs = QIB.query.filter(QIB.idAlbum==album).all()
    elif(album==0 and date!='*'):
        all_qibs = QIB.query.filter(QIB.timeStamp>=datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')).all()
    else:
        all_qibs = QIB.query.all()
    results = qibs_schema.dump(all_qibs)
    return jsonify(results)


@app.route('/get_studies', methods=['GET'])
def yoi():
    album = Album.query.first()
    study = album.study_albums[0].study
    results =study_schema.dump(study)
    return jsonify(results)




################# Helper functions #####################

def get_album_by_name_commited(album_name):
    album = Album.query.filter_by(name = album_name).first()
    if feature_search is None:
        album = Album(album_name,'To be updated')
        db.session.add(album)
        db.session.commit()
        db.session.refresh(album) #get album.id
    return album

def add_qib_for_album_commited(album_id):
    qib = QIB(album_id)
    db.session.add(qib)
    db.session.commit()
    db.session.refresh(qib)
    return qib

def add_modalities(data):
    for i in data["modality"]:
        modality = Modality.query.filter_by(name=i).first()
        if modality is None:
            modality = Modality(i, "To be updated")
            db.session.add(modality)

def add_regions(data):
    for i in data["label"]:
        region = Region.query.filter_by(name=i).first()
        if region is None:
            region = Region(i, "To be updated")
            db.session.add(region)

def add_patients(data):
    patient_frame = data.groupby(['patientID']).mean()
    for i in patient_frame["patientID"]:
        extracted_name = i[:i.index("_")].split(' ')
        first_name = extracted_name[0]
        last_name = extracted_name[1]
        patient = Patient.query.filter_by(first_name=first_name, last_name=last_name).first()
        if patient is None:
            patient = Patient(first_name, last_name, "2000-01-01", "F")
            db.session.add(patient)
            