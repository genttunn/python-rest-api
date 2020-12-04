from feature_manager import app, jsonify,request,models,schemas,db
from pandas import pandas as pd
import json
import os
from pydicom.uid import generate_uid
from datetime import datetime
import random

##################################### INSTANTIATE SCHEMAS #############################################

study_schema = schemas.StudySchema()
studies_schema = schemas.StudySchema(many=True)

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

patient_schema = schemas.PatientSchema()
patients_schema = schemas.PatientSchema(many=True)

########################################################################################################

#################################### MISCHELLANEOUS ####################################################

default_string = "To be updated"
raw_csv_metadata_columns = ['PatientID', 'Modality', 'Label', 'ROI']
custom_csv_metadata_columns = ['PatientName', 'plc_status','Modality','ROI','Series_region']

########################################################################################################

#################################### DEFINE ROUTES  ####################################################

############### ALBUMS

@app.route('/albums', methods=['GET'])
def get_albums():
    try:
        all_albums = models.Album.query.all()
        results = albums_schema.dump(all_albums)
        return jsonify(results)
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")    

@app.route('/albums', methods=['POST'])
def new_album():
    try:
        if request.json:
            content = request.json
            album = models.Album(content['name'],content['description'])
            db.session.add(album)
            db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

@app.route('/albums/<album_id>', methods=['PUT'])
def edit_album(album_id):
    try:
        if request.json:
            content = request.json
            album = models.Album.query.filter_by(id = album_id).first()
            album.name = content['name']
            album.description = content['description']
            db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")


@app.route('/albums/<album_id>', methods=['DELETE'])
def delete_album(album_id):
    try:
        qibs = models.QIB.query.filter_by(id_album = album_id).all()
        print(qibs)
        if len(qibs) > 0: 
            return jsonify("Album has children QIBs. Cannot delete.")
        album = models.Album.query.filter_by(id = album_id).first()
        db.session.delete(album)
        db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

##########################

############### PATIENTS

@app.route('/patients', methods=['GET'])
def get_patients():
    try:
        all_patients = models.Patient.query.all()
        results = patients_schema.dump(all_patients)
        return jsonify(results)
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")    

@app.route('/patients/<patient_id>', methods=['PUT'])
def edit_patient(patient_id):
    try:
        if request.json:
            content = request.json
            patient = models.Patient.query.filter_by(id = patient_id).first()
            patient.first_name = content['first_name']
            patient.last_name = content['last_name']
            patient.birthdate = datetime.strptime(content['birthdate'], '%Y-%m-%d')
            patient.gender = content['gender']
            outcome = models.Outcome.query.filter_by(id_patient = patient_id).first()
            outcome.plc_status = content['plc_status']
            db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")   
 
##########################

############### MODALITIES AND REGIONS
@app.route('/modalities', methods=['GET'])
def get_modalities():
    try:
        all_modalities = models.Modality.query.all()
        results = modalities_schema.dump(all_modalities)
        return jsonify(results)
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")          

@app.route('/regions', methods=['GET'])
def get_regions():
    try:
        all_regions = models.Region.query.all()
        results = regions_schema.dump(all_regions)
        return jsonify(results)
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")   

@app.route('/modalities/<modality_id>', methods=['PUT'])
def edit_modality(modality_id):
    try:
        if request.json:
            content = request.json
            modality = models.Modality.query.filter_by(id = modality_id).first()
            modality.name = content['name']
            modality.description = content['description']
            db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")


@app.route('/regions/<region_id>', methods=['PUT'])
def edit_region(region_id):
    try:
        if request.json:
            content = request.json
            region = models.Region.query.filter_by(id = region_id).first()
            region.name = content['name']
            region.description = content['description']
            db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

##########################

############### FAMILIES AND FEATURES
@app.route('/families_features', methods=['GET'])
def get_families_features():
    try:
        all_families = models.Family.query.all()
        all_features = models.Feature.query.all()
        family_feature_dict = {}
        for family in all_families:
            family_feature_dict[family.name] = []
        for feature in all_features:
            if feature.family.name  in family_feature_dict:
                family_feature_dict[feature.family.name].append(feature_schema.dump(feature))
        family_feature_list = []
        for key, value in family_feature_dict.items():
            result_dict={}
            result_dict["family"] = key
            result_dict["features"] = value
            family_feature_list.append(result_dict)
        return jsonify(family_feature_list)    
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")



@app.route('/features/<feature_id>', methods=['PUT'])
def edit_feature(feature_id):
    try:
        if request.json:
            content = request.json
            feature = models.Feature.query.filter_by(id = feature_id).first()
            feature.name = content['name']
            family = models.Family.query.filter_by(name = content['family']).first()
            feature.family = family
            db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

        
@app.route('/families', methods=['POST'])
def new_family():
    try:
        if request.json:
            content = request.json
            print(content)
            family = models.Family.query.filter_by(name = content['name']).first()
            if family is not None:
                return jsonify("Family already exists.")
            family = models.Family(name = content['name'])
            db.session.add(family)
            db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

@app.route('/families/<family_name>', methods=['PUT'])
def edit_family(family_name):
    try:
        if request.json:
            content = request.json
            family = models.Family.query.filter_by(name = family_name).first()
            family.name = content['name']
            db.session.commit()
            return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")
        
@app.route('/families/<family_name>', methods=['DELETE'])
def delete_family(family_name):
    try:
        family = models.Family.query.filter_by(name = family_name).first()
        features = models.Feature.query.filter_by(id_family = family.id).all()
        if len(features) > 0: 
            return jsonify("This feature family still has features. Cannot delete.")
        db.session.delete(family)
        db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

##########################

############### STUDIES
@app.route('/studies/<album_id>', methods=['GET'])
def get_studies_by_album(album_id):
    try:
        studies = []
        study_albums = models.StudyAlbum.query.filter_by(id_album = album_id).all()
        for study_album in study_albums:
            study = models.Study.query.filter_by(id = study_album.id_study).first()
            studies.append(study)
        results = studies_schema.dump(studies)    
        return jsonify(results)
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

##########################

############### QIBS RELATED

@app.route('/features/<qib_id>', methods=['GET'])
def get_features(qib_id):
    try:
        all_features_of_qib = db.session.query(models.QIBFeature.id_feature).filter(models.QIBFeature.id_qib == qib_id).subquery()
        features = db.session.query(models.Feature).filter(models.Feature.id.in_(all_features_of_qib))
        results = features_schema.dump(features)
        return jsonify(results)
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")
        
@app.route('/qibs/', methods=['GET'])
def get_qibs():
    try:
        album = request.args.get('album', default = 0, type = int)
        region = request.args.get('region', default = 0, type = int)
        date = request.args.get('date', default = '*', type = str)
        print(datetime.now())
        if(album!=0 and region==0 and date=='*'):
            all_qibs = models.QIB.query.filter_by(id_album=album).all()
        elif(album==0 and region!=0 and date=='*'):
            all_qibs = models.QIB.query.join(models.QIBFeature, models.QIB.id == models.QIBFeature.id_qib)\
                .join(models.SeriesRegion, models.QIBFeature.id_series_region == models.SeriesRegion.id)\
                .join(models.Region, models.Region.id == models.SeriesRegion.id_region)\
                .filter(models.Region.id == region).all()
        elif(album==0 and region==0 and date!='*'):
            all_qibs = models.QIB.query.filter(models.QIB.time_stamp >= datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')).all()
        else:
            all_qibs = models.QIB.query.all()
        results = qibs_schema.dump(all_qibs)
        return jsonify(results)
    except Exception as err:
        print(err)
        return jsonify(f"{err.__class__.__name__}: {err}")


@app.route('/qib/<qib_id>', methods=['PUT'])
def edit_qib(qib_id):
    try:
        if request.json:
            content = request.json
            qib = models.QIB.query.filter_by(id = qib_id).first()
            qib.name = content['name']
            qib.description = content['description']
            db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

@app.route('/qib/<qib_id>', methods=['DELETE'])
def delete_qib(qib_id):
    try:
        models.QIB.query.filter_by(id = qib_id).delete()
        db.session.commit()
        return jsonify("OK")
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")
##########################

############### TAG OUTCOMES AND METADATA
@app.route('/qib/tag/<qib_id>', methods=['PUT'])
def tag_column(qib_id):
    try:
        if request.json:
            content = request.json
            print( content['outcome_column'])
            qib = models.QIB.query.filter_by(id = qib_id).first()
            qib.outcome_column = content['outcome_column']
            qib.metadata_columns = content['metadata_columns']
            db.session.commit()
            results = qib_schema.dump(qib)
            return jsonify(results)
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")
##########################

############### GENERATE TABLES, CHARTS AND STATS IN JSON

@app.route('/qib_features/<qib_id>', methods=['GET'])
def get_qib_features_by_qib(qib_id):
    try:
        all_qib_features = models.QIBFeature.query.filter_by(id_qib=qib_id).all()
        df = convert_to_df(all_qib_features)
        return df.to_json(orient='records')
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

@app.route('/statistics/', methods=['GET'])
def get_statistics():
    try:
        series = db.session.query(models.Series.id).count()
        studies = db.session.query(models.Study.id).count()
        patients = db.session.query(models.Patient.id).count()
        qibs = db.session.query(models.QIB.id).count()
        stat_dict = {}
        stat_dict['series'] = series
        stat_dict['studies'] = studies
        stat_dict['patients'] = patients
        stat_dict['qibs'] = qibs
        return jsonify(stat_dict)
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

@app.route('/chart/scatterplot/<qib_id>/<feature_1>/<feature_2>', methods=['GET'])
def generate_scatterplot_data(qib_id, feature_1, feature_2):
    try:
        feature_1 = models.Feature.query.filter_by(id = feature_1).scalar()
        feature_2 = models.Feature.query.filter_by(id = feature_2).scalar()
        all_qib_features = models.QIBFeature.query.filter(models.QIBFeature.id_qib == qib_id)\
            .filter((models.QIBFeature.feature == feature_1) | (models.QIBFeature.feature == feature_2)).all()
        df = convert_to_scatter_coords(all_qib_features,feature_1,feature_2)
        return df.to_json(orient='values')
    except Exception as err:
        return jsonify(f"{err.__class__.__name__}: {err}")

##########################

############### UPLOAD CSV
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    try:
        file_name=''
        album_name=''  
        qib_name=''
        qib_description=''
        csv_type=''
        if request.form:
            album_name = request.form['album_name']
            qib_name = request.form['qib_name']
            qib_description = request.form['qib_description']
            file_name = request.form['file_name']
            csv_type = request.form['csv_type']
        if request.method == 'POST' and request.files:
            data = pd.read_csv(request.files[file_name])
            headers = data.columns.values.tolist()
            csv_check = check_headers(headers, csv_type)
            if csv_check == False:
                return jsonify('Invalid columns')
            else:
                if csv_type == 'Custom QIB':
                    load_custom_filter_csv_to_db(data,album_name, qib_name,qib_description) 
                if csv_type == 'New QIB':
                    load_file_to_db(data,album_name,qib_name,qib_description)
                if csv_type == 'Outcome list':
                    add_outcome(data)
        return jsonify('OK')
    except Exception:
        return jsonify(f"{err.__class__.__name__}: {err}")

##########################

@app.route('/', methods=['GET'])
def greet():
    return jsonify('Hello. This is the API for the feature manager.')
########################################################################################################

########################################### HELPER FUNCTIONS ##########################################
def check_headers(headers, csv_type):
    result = False
    list_new_qib = ['PatientID', 'Modality', 'ROI']
    list_patient_outcome = ['patient_id', 'plc_status']
    list_custom_qib = ['PatientName', 'plc_status', 'Modality', 'ROI', 'Series_region']
    if csv_type == 'New QIB':
        result = all(elem in headers  for elem in list_new_qib)
    if csv_type == 'Custom QIB':
        result = all(elem in headers  for elem in list_custom_qib)
    if csv_type == 'Outcome list':
        result = all(elem in headers  for elem in list_patient_outcome)
    return result
#convert to DataFrame
def convert_to_df(qib_feature_set):
    current_feature_name = ''
    feature_dict = {}
    feature_dict['PatientName'] = []
    feature_dict['plc_status'] = []
    feature_dict['Modality'] = []
    feature_dict['ROI'] = []
    feature_dict['Series_region']=[]
    count=0
    for qb in qib_feature_set:
        if(qb.feature.name != current_feature_name):
            current_feature_name = qb.feature.name
            count+=1
            feature_dict[current_feature_name] = []
        if current_feature_name in feature_dict:
            feature_dict[current_feature_name].append(qb.feature_value)
            if(count<2):
                feature_dict['PatientName'].append(qb.series_region.series.study.patient.first_name + '_' + qb.series_region.series.study.patient.last_name)
                feature_dict['plc_status'].append(qb.series_region.series.study.patient.outcome.plc_status)
                feature_dict['Modality'].append(qb.series_region.series.modality.name)
                feature_dict['ROI'].append(qb.series_region.region.name)
                feature_dict['Series_region'].append(qb.series_region.id)
    df = pd.DataFrame(data=feature_dict)
    return df

def convert_to_scatter_coords(qib_features, feature_1, feature_2):
    feature_dict = {}
    feature_dict[feature_1.name] = [feature_1.name]
    feature_dict[feature_2.name] = [feature_2.name]
    feature_dict['plc_status'] = ['plc_status']
    for qf in qib_features:
        plc_status = qf.series_region.series.study.patient.outcome.plc_status
        if qf.feature == feature_1: 
            feature_dict[feature_1.name].append(qf.feature_value)
            feature_dict['plc_status'].append(plc_status)
        elif qf.feature == feature_2: 
            feature_dict[feature_2.name].append(qf.feature_value)
    df = pd.DataFrame(data=feature_dict)
    return df
########################################################################################################

########################################### CSV ETL PROCESS ############################################
# Load csv
def get_album_by_name_commited(album_name):
    print('get_album_by_name_commited')
    album = models.Album.query.filter_by(name = album_name).first()
    if album is None:
        album = models.Album(album_name,'To be updated')
        db.session.add(album)
        db.session.commit()
        db.session.refresh(album)
    return album

def add_qib_for_album_commited(album_id,qib_name,qib_description):
    print('add_qib_for_album_commited')
    qib = models.QIB(album_id,qib_name,qib_description)
    db.session.add(qib)
    db.session.commit()
    db.session.refresh(qib)
    return qib

def add_modalities(data):
    print('add_modalities')
    for i in data["Modality"]:
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
    patient_column_name = ''
    if 'PatientName' in data.columns:
        patient_column_name = 'PatientName'
    elif 'PatientID' in data.columns:
        patient_column_name = 'PatientID'
    for i in data[patient_column_name]:
        extracted_name = i.split('_') 
        first_name = extracted_name[0]
        # Last name is used as patient number for outcome list
        last_name = extracted_name[1]
        patient = models.Patient.query.filter_by(last_name=last_name).first()
        if patient is None:
            patient = models.Patient(first_name=first_name, last_name=last_name, birthdate=datetime.strptime('2000-01-01', '%Y-%m-%d'),gender= 'F')
            db.session.add(patient)
            db.session.flush()
            add_mock_studies_for_patient(patient.id)
    

def add_features(data , family):
    print('add_feature')
    family = models.Family.query.filter_by(name=family).first()
    for i in data.columns:
        feature = models.Feature.query.filter_by(name=i).first()
        if feature is None and i not in raw_csv_metadata_columns  and i not in custom_csv_metadata_columns:
            feature = models.Feature( name = i , id_family = family.id)
            db.session.add(feature)


def add_series_and_studies_commit(data, album):
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
        study_album = models.StudyAlbum.query.filter_by(id_study = random_study.id , id_album = album.id).first()
        if study_album is None:
                study_album = models.StudyAlbum(id_study = random_study.id , id_album = album.id)
                db.session.add(study_album)
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
    data_out['Series_region'] = series_region_column
    return data_out
# uses patient.last_name as number of reference
def add_outcome(data):
    print('add_outcome')
    for index, row in data.iterrows():
        patient = models.Patient.query.filter_by(last_name=row.patient_id).first()
        if patient != None:
            outcome = models.Outcome.query.filter_by(id_patient = patient.id).first()
            if outcome is None:
                outcome = models.Outcome(plc_status = row.plc_status, id_patient = patient.id)
            else:
                outcome.plc_status = row.plc_status
            db.session.add(outcome)
    db.session.commit()


def add_qib_features_commit(data, qib_id):
    print('add_qib_features')
    series_region = []
    for i in data["Series_region"]:
        series_region.append(i)
    for i in data.columns:
        index_series_region = 0
        feature = models.Feature.query.filter_by(name=i).first()
        if feature != None:
            for a in data[i]:
                qf = models.QIBFeature(id_qib = qib_id, id_feature =  feature.id,feature_value = a, id_series_region = series_region[index_series_region])
                db.session.add(qf)
                index_series_region += 1
    db.session.commit()

########################################################################################################

########################################### LOAD CSV, INSERT DATA ############################################
def load_file_to_db(data,album_name,qib_name,qib_description):
    print('load raw feature set')
    family = models.Family.query.filter_by(id=1).first()
    album = get_album_by_name_commited(album_name)
    qib = add_qib_for_album_commited(album.id,qib_name,qib_description)
    add_modalities(data)
    add_regions(data)
    add_patients(data)
    add_features(data,family.name)
    db.session.commit()
    data_appended = add_series_and_studies_commit(data, album)
    add_qib_features_commit(data_appended, qib.id)

def load_custom_filter_csv_to_db(data,album_name, qib_name,qib_description):
    print('load custom filter')
    family = models.Family.query.filter_by(id=1).first()
    album = get_album_by_name_commited(album_name)
    qib = add_qib_for_album_commited(album.id,qib_name,qib_description)
    add_modalities(data)
    add_regions(data)
    add_patients(data)
    add_features(data,family.name)
    db.session.commit()
    add_qib_features_commit(data, qib.id)

def stock_albums():
    alb1 = models.Album(name = "album_1", description = "album one")
    alb2 = models.Album(name = "album_2", description = "album two")
    alb3 = models.Album(name = "custom_qibs", description = "for saved searches")
    db.session.add(alb1)
    db.session.add(alb2)
    db.session.add(alb3)
    db.session.commit()

def stock_families():
    family_texture = models.Family(name='texture')
    family_intensity = models.Family(name='intensity')
    db.session.add(family_texture)
    db.session.add(family_intensity)
    db.session.commit()
# Add some default albums, feature families, and qibs
def quick_start():
    print('add some default albums and feature families')
    stock_albums()
    stock_families()
    data_csv = pd.read_csv("./csv/features_album_Lymphangitis_Texture-Intensity_CT_GTV_L.csv")
    load_file_to_db(data_csv,'album_1','default_qib_1','CT_GTV_L')
    data_csv = pd.read_csv("./csv/features_album_Lymphangitis_Texture-Intensity_CT_GTV_N.csv")
    load_file_to_db(data_csv,'album_1','default_qib_2','CT_GTV_N')
    data_csv =  pd.read_csv("./csv/list_patients_outcome.csv")
    add_outcome(data_csv)

########################################################################################################


