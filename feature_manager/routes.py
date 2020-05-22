from feature_manager import app, jsonify,request
from feature_manager.models import *
from feature_manager.schemas import *
from pandas import pandas as pd
import json
import os

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

data_csv = pd.read_csv("./csv/features_texture.csv")
current_dir = str(os.path.abspath(os.path.dirname(__file__)))



@app.route('/albums', methods=['GET'])
def get_albums():
    all_albums = Album.query.all()
    results = albums_schema.dump(all_albums)
    return jsonify(results)

@app.route('/qibs/', methods=['GET'])
def get_qibs():
    album = request.args.get('album', default = 0, type = int)
    date = request.args.get('date', default = '*', type = str)
    print(datetime.now())
    if(album!=0 and date=='*'):
        all_qibs = QIB.query.filter_by(id_album=album).all()
    elif(album==0 and date!='*'):
        all_qibs = QIB.query.filter(QIB.time_stamp >= datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')).all()
    else:
        all_qibs = QIB.query.all()
    results = qibs_schema.dump(all_qibs)
    return jsonify(results)

@app.route('/qib_features/<qib_id>', methods=['GET'])
def get_qib_features_by_qib(qib_id):
    all_qib_features = QIBFeature.query.filter_by(id_qib=qib_id).all()
    df = convert_to_df(all_qib_features)
    results = []
    for i in df.columns:
        new_dict = {}
        new_dict['column_name'] = i
        values = []
        for a in df[i]:
            values.append(a)
        new_dict['values'] = values
        results.append(new_dict)
    return jsonify(results)


@app.route('/generate_csv/<qib_id>', methods=['POST'])
def generate_csv_by_feature(qib_id):
    data = request.json
    features = data['features']
    feature_list = features[1:].split(',')
    file_dir = generate_qib_csv(feature_list)
    res = {}
    res['path'] = file_dir
    return  jsonify(res)

@app.route("/", methods=['GET'])
def hello():
    return 'Hello'



################# Helper functions #####################
def convert_to_df(qib_feature_set):
    current_feature_name = ''
    feature_dict = {}
    feature_dict['modality'] = []
    feature_dict['label'] = []
    count=0
    for qb in qib_feature_set:
        if(qb.feature.name != current_feature_name):
            current_feature_name = qb.feature.name
            count+=1
            feature_dict[current_feature_name] = []
        if current_feature_name in feature_dict:
            feature_dict[current_feature_name].append(qb.feature_value)
            if(count<2):
                feature_dict['modality'].append(qb.series_region.series.modality.name)
                feature_dict['label'].append(qb.series_region.region.name)
    df = pd.DataFrame(data=feature_dict)
    return df

def get_album_by_name_commited(album_name):
    print('get_album_by_name_commited')
    album = Album.query.filter_by(name = album_name).first()
    if album is None:
        album = Album(album_name,'To be updated')
        db.session.add(album)
        db.session.commit()
        db.session.refresh(album) #get album.id
    print(album.name)
    return album

def add_qib_for_album_commited(album_id):
    print('add_qib_for_album_commited')
    qib = QIB(album_id)
    db.session.add(qib)
    db.session.commit()
    db.session.refresh(qib)
    print(qib.id)
    return qib

def add_modalities(data):
    print('add_modalities')
    for i in data["modality"]:
        print(i)
        modality = Modality.query.filter_by(name=i).first()
        if modality is None:
            modality = Modality(name = i)
            db.session.add(modality)

def add_regions(data):
    print('add_regions')
    for i in data["label"]:
        region = Region.query.filter_by(name=i).first()
        if region is None:
            region = Region(name = i)
            db.session.add(region)

def add_patients(data):
    print('add_patients')
    for i in data["patientID"]:
        extracted_name = i[:i.index("_")].split(' ')
        first_name = extracted_name[0]
        last_name = extracted_name[1]
        patient = Patient.query.filter_by(first_name=first_name, last_name=last_name).first()
        if patient is None:
            patient = Patient(first_name=first_name, last_name=last_name, birthdate='2000-01-01',gender= 'F')
            db.session.add(patient)

def add_features(data , family):
    print('add_feature')
    family = Family.query.filter_by(name=family).first()
    for i in data.columns:
        feature = Feature.query.filter_by(name=i).first()
        if feature is None and i not in ['patientID', 'modality', 'label']:
            feature = Feature( name = i , id_family = family.id)
            db.session.add(feature)

def add_studies_and_series_commit(data,album):
    print('add_studies_and_series')
    data_out = data
    series_region_column=[]
    series_column=[]
    study_column=[]
    
    current_patient_value = ''
    current_modality_value = ''

    current_study = ''
    current_series = ''
    for index, row in data.iterrows():
        if(row.patientID != current_patient_value):
            current_patient_value = row.patientID
            extracted_name = row.patientID[:row.patientID.index("_")].split(' ')
            first_name = extracted_name[0]
            last_name = extracted_name[1]
            patient = Patient.query.filter_by(first_name=first_name, last_name=last_name).first()
            study = Study.query.filter_by(name = row.patientID[row.patientID.index("_"):] ,id_patient = patient.id).first()
            if study is None:
                study = Study(name = row.patientID[row.patientID.index("_"):] ,id_patient = patient.id)
                db.session.add(study)
                db.session.flush()
            study_album = StudyAlbum.query.filter_by(id_study = study.id , id_album = album.id).first()
            if study_album is None:
                study_album = StudyAlbum(id_study = study.id , id_album = album.id)
                db.session.add(study_album)
            current_study = study
        if(row.modality != current_modality_value):
            current_modality_value = row.modality
            modality = Modality.query.filter_by(name = row.modality).first()
            series = Series(sickness='To be updated', id_study = current_study.id, id_modality = modality.id)
            db.session.add(series)
            db.session.flush()
            current_series = series
        print('done adding series and studies')
        region = Region.query.filter_by(name = row.label).first()
        series_region = SeriesRegion(id_series = current_series.id, id_region = region.id)
        db.session.add(series_region)
        db.session.flush()
        
        series_region_column.append(series_region.id)
        series_column.append(current_series.id)
        study_column.append(current_study.id)

        print(series_region_column)
        print(series_column)
        print(study_column)
        
    db.session.commit()
    data_out['series_region'] = series_region_column
    data_out['series'] = series_column
    data_out['study'] = study_column

    return data_out

def add_qib_features_commit(data, qib_id):
    print('add_qib_features')
    series_region = []
    for i in data["series_region"]:
        series_region.append(i)
    for i in data.columns:
        index_series_region = 0
        feature = Feature.query.filter_by(name=i).first()
        if feature != None:
            print(feature.id)
            for a in data[i]:
                print(str(a) + '     ' + str(series_region[index_series_region]))
                qf = QIBFeature(id_qib = qib_id, id_feature =  feature.id,feature_value = a, id_series_region = series_region[index_series_region])
                db.session.add(qf)
                index_series_region += 1
    db.session.commit()

def load_file_to_db(data,album_name,family):
    album = get_album_by_name_commited(album_name)
    qib = add_qib_for_album_commited(album.id)
    add_modalities(data)
    add_regions(data)
    add_patients(data)
    add_features(data,family)
    db.session.commit()
    data_appended = add_studies_and_series_commit(data,album)
    add_qib_features_commit(data_appended, qib.id)

    
def insert_data():
    family_texture = Family(name='texture')
    family_intensity = Family(name='intensity')
    db.session.add(family_texture)
    db.session.add(family_intensity)
    db.session.commit()
    data_csv = pd.read_csv("./csv/features_intensity.csv")
    load_file_to_db(data_csv,'test_album_1','intensity')
    data_csv = pd.read_csv("./csv/features_texture.csv")
    load_file_to_db(data_csv,'test_album_2','texture')

def generate_qib_csv(feature_list):
    feature_dict = {}
    all_qib_features = QIBFeature.query.filter_by(id_qib=1).all()
    current_feature_name = ''
    feature_dict['modality'] = []
    feature_dict['label'] = []
    count = 0 
    for qb in all_qib_features:
        if(qb.feature.name != current_feature_name):
            current_feature_name = qb.feature.name
            if current_feature_name in feature_list:
                count+=1
                feature_dict[current_feature_name] = []
        if current_feature_name in feature_dict:
            feature_dict[current_feature_name].append(qb.feature_value)
            if(count<2):
                feature_dict['modality'].append(qb.series_region.series.modality.name)
                feature_dict['label'].append(qb.series_region.region.name)
    print(feature_dict)
    df = pd.DataFrame(data=feature_dict)
    print(df)
    file = current_dir + f"\\data\\{str(datetime.now().timestamp())}.csv"
    df.to_csv(file, index=False)
    return file



# def test_gen_modality():
#     feature_dict = {}
#     feature_dict['modality'] = []
#     feature_dict['label'] = []
#     all_qib_features = db.session.query(QIBFeature).filter(QIBFeature.series_region.has(SeriesRegion.id_region == 1))
#     current_feature_name = ''
#     count = 0 
#     for qb in all_qib_features:
#         if(qb.feature.name != current_feature_name):
#             current_feature_name = qb.feature.name
#             feature_dict[current_feature_name] = []
#         if current_feature_name in feature_dict:
#             feature_dict[current_feature_name].append(qb.feature_value)
#             feature_dict['modality'].append(qb.series_region.series.modality.name)
#             feature_dict['label'].append(qb.series_region.region.name)
#     print(feature_dict)


# @app.route("/test", methods=['GET'])
# def test():
#     all_families = Family.query.all()
#     results = families_schema.dump(all_families)
#     return jsonify(results)

# @app.route("/test_features", methods=['GET'])
# def test_features():
#     all_features = Feature.query.all()
#     results = features_schema.dump(all_features)
#     return jsonify(results)

# @app.route('/qib_features/<qib_id>', methods=['GET'])
# def get_qib_features_by_qib(qib_id):
#     all_qib_features = QIBFeature.query.filter_by(idQIB=qib_id).all()
#     results = qib_features_schema.dump(all_qib_features)
#     return jsonify(results)


# @app.route('/qibs/', methods=['GET'])
# def get_qibs():
#     album = request.args.get('album', default = 0, type = int)
#     date = request.args.get('date', default = '*', type = str)
#     if(album!=0 and date=='*'):
#         all_qibs = QIB.query.filter(QIB.idAlbum==album).all()
#     elif(album==0 and date!='*'):
#         all_qibs = QIB.query.filter(QIB.timeStamp>=datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')).all()
#     else:
#         all_qibs = QIB.query.all()
#     results = qibs_schema.dump(all_qibs)
#     return jsonify(results)


# @app.route('/get_studies', methods=['GET'])
# def yoi():
#     album = Album.query.first()
#     study = album.study_albums[0].study
#     results =study_schema.dump(study)
#     return jsonify(results)