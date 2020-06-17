from feature_manager import app, jsonify,request,models,schemas,db
from pandas import pandas as pd
import json
import os
from pydicom.uid import generate_uid
from datetime import datetime
import random
region_schema = schemas.RegionSchema()
regions_schema = schemas.RegionSchema(many=True)
modality_schema = schemas.ModalitySchema()
modalities_schema = schemas.ModalitySchema(many=True)
family_schema = schemas.FamilySchema()
families_schema = schemas.FamilySchema(many=True)
feature_schema = schemas.FeatureSchema()
features_schema = schemas.FeatureSchema(many=True)
qib_feature_schema = schemas.QIBFeatureSchema()
qib_features_schema = schemas.QIBFeatureSchema(many=True)
qib_schema = schemas.QIBSchema()
qibs_schema = schemas.QIBSchema(many=True)

album_schema = schemas.AlbumSchema()
albums_schema = schemas.AlbumSchema(many=True)


data_csv = pd.read_csv("./csv/features_texture.csv")
current_dir = str(os.path.abspath(os.path.dirname(__file__)))

default_string = "To be updated"


@app.route('/albums', methods=['GET'])
def get_albums():
    all_albums = models.Album.query.all()
    results = albums_schema.dump(all_albums)
    return jsonify(results)

@app.route('/region', methods=['GET'])
def get_regions():
    regions = models.Region.query.all()
    results = regions_schema.dump(regions)
    return jsonify(results)

@app.route('/region/<region_id>', methods=['GET'])
def get_region(region_id):
    region = models.Region.query.filter_by(id = region_id).first()
    results = region_schema.dump(region)
    return jsonify(results)


@app.route('/modality', methods=['GET'])
def get_modalities():
    modalities = models.Modality.query.all()
    results = modalities_schema.dump(modalities)
    return jsonify(results)

@app.route('/modality/<modality_id>', methods=['GET'])
def get_modality(modality_id):
    modality = models.Modality.query.filter_by(id = modality_id).first()
    results = modality_schema.dump(modality)
    return jsonify(results)

@app.route('/qibs/', methods=['GET'])
def get_qibs():
    album = request.args.get('album', default = 0, type = int)
    region = request.args.get('region', default = 0, type = int)
    date = request.args.get('date', default = '*', type = str)
    print(datetime.now())
    if(album!=0 and region==0 and date=='*'):
        all_qibs = models.QIB.query.filter_by(id_album=album).all()
    elif(album==0 and region!=0 and date=='*'):
        all_qibs = models.QIB.query.join(models.QIBFeature, models.QIB.id == models.QIBFeature.id_qib).join(models.SeriesRegion, models.QIBFeature.id_series_region == models.SeriesRegion.id).join(models.Region, models.Region.id == models.SeriesRegion.id_region).filter(models.Region.id == region).all()
    elif(album==0 and region==0 and date!='*'):
        all_qibs = models.QIB.query.filter(models.QIB.time_stamp >= datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')).all()
    else:
        all_qibs = models.QIB.query.all()
    results = qibs_schema.dump(all_qibs)
    return jsonify(results)

@app.route('/qib_features/qib/<qib_id>', methods=['GET'])
def get_qib_features_by_qib(qib_id):
    all_qib_features = models.QIBFeature.query.filter_by(id_qib=qib_id).all()
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
    return df.to_json(orient='records')
    # return jsonify(results)

@app.route('/qib_features/region/<region_id>', methods=['GET'])
def get_qib_features_by_region(region_id):
    region = models.Region.query.filter_by(id = region_id).first()
    if region != None:
        all_qib_features = models.QIBFeature.query.filter(models.QIBFeature.series_region.has(models.SeriesRegion.id_region == region.id)).all()
        print(len(all_qib_features))
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


@app.route('/qib_features/modality/<modality_id>', methods=['GET'])
def get_qib_features_by_modality(modality_id):
    modality = models.Modality.query.filter_by(id = modality_id).first()
    if modality != None:
        #  = s.query(Parent).join(Child, Parent.child).filter(Child.value > 20)
        all_qib_features = models.QIBFeature.query.join(models.SeriesRegion, models.QIBFeature.id_series_region == models.SeriesRegion.id).join(models.Series, models.SeriesRegion.id_series == models.Series.id).filter(models.Series.id_modality == modality.id).all()
        print(len(all_qib_features))
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

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    try:
        file_name=''
        album_name=''
        family=''
        qib_name=''
        qib_description=''
        if request.form:
            album_name = request.form['album_name']
            family = request.form['family']
            qib_name = request.form['qib_name']
            qib_description = request.form['qib_description']
            file_name = request.form['file_name']
            print(f"{file_name} {album_name} {family} {qib_name} {qib_description}")
            print(request.files)
        if request.method == 'POST' and request.files:
            print('yes')
            data = pd.read_csv(request.files[file_name])
            load_file_to_db(data,album_name,family,qib_name,qib_description)
            print(data)
        return 'Upload ok'
    except Exception:
        return 'Upload failed'

@app.route('/studies/<album_id>', methods=['GET'])
def get_studies_by_album(album_id):
    studies = []
    study_albums = models.StudyAlbum.query.filter_by(id_album=album_id).all()
    for sa in study_albums:
        study = sa.study
        studies.append(study)
    results = models.studies_schema.dump(studies)
    return jsonify(results)

@app.route("/", methods=['GET'])
def hello():
    return 'Hello'



################# Helper functions #####################
def convert_to_df(qib_feature_set):
    current_feature_name = ''
    feature_dict = {}
    feature_dict['patientName'] = []
    feature_dict['plc_status'] = []
    feature_dict['modality'] = []
    feature_dict['ROI'] = []
    
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
                feature_dict['ROI'].append(qb.series_region.region.name)
                feature_dict['patientName'].append(qb.series_region.series.study.patient.first_name + '_' + qb.series_region.series.study.patient.last_name)
                feature_dict['plc_status'].append(qb.series_region.series.study.patient.outcome.plc_status)
    print(len(feature_dict['modality']))
    print(len(feature_dict['ROI']))
    print(len(feature_dict['patientName']))
    print(len(feature_dict['plc_status']))
    df = pd.DataFrame(data=feature_dict)
    return df


# load csv
def get_album_by_name_commited(album_name):
    print('get_album_by_name_commited')
    album = models.Album.query.filter_by(name = album_name).first()
    if album is None:
        album = models.Album(album_name,'To be updated')
        db.session.add(album)
        db.session.commit()
        db.session.refresh(album) #get album.id
    print(album.name)
    return album

def add_qib_for_album_commited(album_id,qib_name,qib_description):
    print('add_qib_for_album_commited')
    qib = models.QIB(album_id,qib_name,qib_description)
    db.session.add(qib)
    db.session.commit()
    db.session.refresh(qib)
    print(qib.id)
    return qib

def add_modalities(data):
    print('add_modalities')
    for i in data["Modality"]:
        print(i)
        modality = models.Modality.query.filter_by(name=i).first()
        if modality is None:
            modality = models.Modality(name = i)
            db.session.add(modality)

def add_regions(data):
    print('add_regions')
    for i in data["ROI"]:
        region = models.Region.query.filter_by(name=i).first()
        if region is None:
            region = models.Region(name = i)
            db.session.add(region)

def add_mock_studies_for_patient(patient_id):
    study_1 = models.Study(id_patient = patient_id, name = f"Study 1 (Patient ID: {patient_id})")
    study_2 = models.Study(id_patient = patient_id, name = f"Study 2 (Patient ID: {patient_id})")
    study_3 = models.Study(id_patient = patient_id, name = f"Study 3 (Patient ID: {patient_id})")
    db.session.add(study_1)
    db.session.add(study_2)
    db.session.add(study_3)

def add_patients(data):
    # ex: PatientLC_16_20161005
    print('add_patients')
    for i in data["PatientID"]:
        extracted_name = i.split('_') 
        first_name = extracted_name[0]
        # we use last name as patient number for now, update later
        last_name = extracted_name[1]
        patient = models.Patient.query.filter_by(first_name=first_name, last_name=last_name).first()
        if patient is None:
            patient = models.Patient(first_name=first_name, last_name=last_name, birthdate='2000-01-01',gender= 'F')
            db.session.add(patient)
            db.session.flush()
            add_mock_studies_for_patient(patient.id)



def add_features(data , family):
    print('add_feature')
    family = models.Family.query.filter_by(name=family).first()
    for i in data.columns:
        feature = models.Feature.query.filter_by(name=i).first()
        if feature is None and i not in ['PatientID', 'Modality', 'Label', 'ROI']:
            feature = models.Feature( name = i , id_family = family.id)
            db.session.add(feature)

def add_series_and_studies_commit(data):
    print('add_series_and_studies')
    data_out = data
    study_column = []
    series_column=[]
    series_region_column=[]
    for index, row in data.iterrows():
        #get Patient
        extracted_name = row.PatientID.split('_') 
        last_name = extracted_name[1]
        patient = models.Patient.query.filter_by(last_name=last_name).first()
        #get random Study of Patient
        studies = models.Study.query.filter_by(id_patient = patient.id)
        row_count = int(studies.count())
        random_study = studies.offset(int(row_count*random.random())).first()
        print(f"Random study number: {random_study.name}")
        #create Series for Study
        modality = models.Modality.query.filter_by(name = row.Modality).first()
        series = models.Series.query.filter_by(name = row.PatientID, id_modality = modality.id,id_study = random_study.id).first()
        if series is None:
            series = models.Series(name = row.PatientID, id_modality = modality.id,id_study = random_study.id, series_uid = str(generate_uid()))
            db.session.add(series)
            db.session.flush()
        region = models.Region.query.filter_by(name = row.ROI).first()
        series_region = models.SeriesRegion(id_series = series.id, id_region = region.id)
        db.session.add(series_region)
        db.session.flush()
        study_column.append(random_study.id)
        series_column.append(series.id)
        series_region_column.append(series_region.id)
    db.session.commit()
    data_out['study'] = study_column
    data_out['series'] = series_column
    data_out['series_region'] = series_region_column
    
    return data_out
def testy():
    data = pd.read_csv("./csv/features_album_Lymphangitis_Texture-Intensity_PT_GTV_N.csv")
    for index, row in data.iterrows():
        series = models.Series.query.filter_by(name = row.PatientID).first()
        extracted_name = row.PatientID.split('_') 
        last_name = extracted_name[1]
        patient = models.Patient.query.filter_by(last_name=last_name).first()

        modality = models.Modality.query.filter_by(name = row.Modality).first()
        print(modality.name)

def random_study(patient_id):
    patient = models.Patient.query.filter_by(id=patient_id).first()
    print(f"patient: {patient.last_name}")
    studies = models.Study.query.filter_by(id_patient = patient.id)
    print(studies)
    row_count = int(studies.count())
    print(row_count)
    rand = random.randrange(0, row_count) 
    random_study = db.session.query(models.Study)[rand]
    print(f"Random study number: {random_study.name}")

#  from feature_manager.routes import *

def add_outcome(data):
    for index, row in data.iterrows():
        patient = models.Patient.query.filter_by(last_name=row.patient_id).first()
        if patient != None:
            outcome = models.Outcome(plc_status = row.plc_status, id_patient = patient.id)
            db.session.add(outcome)
    db.session.commit()



def add_qib_features_commit(data, qib_id):
    print('add_qib_features')
    series_region = []
    for i in data["series_region"]:
        series_region.append(i)
    for i in data.columns:
        index_series_region = 0
        feature = models.Feature.query.filter_by(name=i).first()
        if feature != None:
            print(feature.id)
            for a in data[i]:
                print(str(a) + '     ' + str(series_region[index_series_region]))
                qf = models.QIBFeature(id_qib = qib_id, id_feature =  feature.id,feature_value = a, id_series_region = series_region[index_series_region])
                db.session.add(qf)
                index_series_region += 1
    db.session.commit()

def load_file_to_db(data,album_name,family,qib_name,qib_description):
    album = get_album_by_name_commited(album_name)
    qib = add_qib_for_album_commited(album.id,qib_name,qib_description)
    add_modalities(data)
    add_regions(data)
    add_patients(data)
    add_features(data,family)
    db.session.commit()
    data_appended = add_series_and_studies_commit(data)
    add_qib_features_commit(data_appended, qib.id)

def custom_album():
    alb = models.Album(name = "custom_qibs", description = "for saved searches")
    db.session.add(alb)
    db.session.commit()

def insert_data():
    family_texture = models.Family.query.filter_by(name='texture').first()
    family_intensity = models.Family.query.filter_by(name='intensity').first()
    if family_texture is None or family_intensity is None:
        family_texture = models.Family(name='texture')
        family_intensity = models.Family(name='intensity')
        db.session.add(family_texture)
        db.session.add(family_intensity)
        db.session.commit()
    data_csv = pd.read_csv("./csv/features_album_Lymphangitis_Texture-Intensity_CT_GTV_L.csv")
    load_file_to_db(data_csv,'test_album_1','intensity',default_string,default_string)
    data_csv = pd.read_csv("./csv/features_album_Lymphangitis_Texture-Intensity_CT_GTV_N.csv")
    load_file_to_db(data_csv,'test_album_2','texture',default_string,default_string)
    data_csv = pd.read_csv("./csv/features_album_Lymphangitis_Texture-Intensity_CT_GTV_T.csv")
    load_file_to_db(data_csv,'test_album_2','texture',default_string,default_string)

    data_csv = pd.read_csv("./csv/features_album_Lymphangitis_Texture-Intensity_PT_GTV_L.csv")
    load_file_to_db(data_csv,'test_album_1','intensity',default_string,default_string)
    data_csv = pd.read_csv("./csv/features_album_Lymphangitis_Texture-Intensity_PT_GTV_N.csv")
    load_file_to_db(data_csv,'test_album_2','texture',default_string,default_string)
    data_csv = pd.read_csv("./csv/features_album_Lymphangitis_Texture-Intensity_PT_GTV_T.csv")
    load_file_to_db(data_csv,'test_album_2','texture',default_string,default_string)
    data_csv =  pd.read_csv("./csv/list_patients.csv")
    add_outcome(data_csv)

def generate_qib_csv(feature_list):
    feature_dict = {}
    all_qib_features = models.QIBFeature.query.filter_by(id_qib=1).all()
    current_feature_name = ''
    feature_dict['patientName'] = []
    feature_dict['plc_status'] = []
    feature_dict['modality'] = []
    feature_dict['ROI'] = []
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
                feature_dict['ROI'].append(qb.series_region.region.name)
                feature_dict['patientName'].append(qb.series_region.series.study.patient.first_name + '_' + qb.series_region.series.study.patient.last_name)
                feature_dict['plc_status'].append(qb.series_region.series.study.patient.outcome.plc_status)
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

# def add_studies_and_series_commit(data,album):
#     print('add_studies_and_series')
#     data_out = data
#     series_region_column=[]
#     series_column=[]
#     study_column=[]
    
#     current_patient_value = ''
#     current_modality_value = ''

#     current_study = ''
#     current_series = ''
#     for index, row in data.iterrows():
#         if(row.patientID != current_patient_value):
#             current_patient_value = row.patientID
#             extracted_name = row.patientID[:row.patientID.index("_")].split(' ')
#             first_name = extracted_name[0]
#             last_name = extracted_name[1]
#             patient = Patient.query.filter_by(first_name=first_name, last_name=last_name).first()
#             study = Study.query.filter_by(name = row.patientID[row.patientID.index("_"):] ,id_patient = patient.id).first()
#             if study is None:
#                 study = Study(name = row.patientID[row.patientID.index("_"):] ,id_patient = patient.id)
#                 db.session.add(study)
#                 db.session.flush()
#             study_album = StudyAlbum.query.filter_by(id_study = study.id , id_album = album.id).first()
#             if study_album is None:
#                 study_album = StudyAlbum(id_study = study.id , id_album = album.id)
#                 db.session.add(study_album)
#             current_study = study
#         if(row.modality != current_modality_value):
#             current_modality_value = row.modality
#             modality = Modality.query.filter_by(name = row.modality).first()
#             series = Series(sickness='To be updated', id_study = current_study.id, id_modality = modality.id)
#             db.session.add(series)
#             db.session.flush()
#             current_series = series
#         print('done adding series and studies')
#         region = Region.query.filter_by(name = row.label).first()
#         series_region = SeriesRegion(id_series = current_series.id, id_region = region.id)
#         db.session.add(series_region)
#         db.session.flush()
        
#         series_region_column.append(series_region.id)
#         series_column.append(current_series.id)
#         study_column.append(current_study.id)

#         print(series_region_column)
#         print(series_column)
#         print(study_column)
        
#     db.session.commit()
#     data_out['series_region'] = series_region_column
#     data_out['series'] = series_column
#     data_out['study'] = study_column

#     return data_out

