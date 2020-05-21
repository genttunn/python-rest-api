from feature_manager import db
from datetime import datetime



class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    birthdate = db.Column(db.DateTime)
    gender = db.Column(db.String(2))


class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_patient= db.Column(db.Integer,  db.ForeignKey('patient.id'))
    time_stamp = db.Column(db.DateTime, default = datetime.now())
    patient = db.relationship('Patient', backref='study')



class StudyAlbum(db.Model):
    id_study = db.Column(db.Integer, db.ForeignKey('study.id'),primary_key=True)
    id_album = db.Column(db.Integer, db.ForeignKey(
        'album.id'),primary_key=True)
    study = db.relationship('Study', backref='study_album')
    album = db.relationship('Album', backref='study_album')

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    time_stamp = db.Column(db.DateTime, default = datetime.now())
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.time_stamp = datetime.now()

class Modality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))

    # id_qib_feature = db.Column(db.Integer, db.ForeignKey('qib_feature.id'))
    # id_patient= db.Column(db.Integer,  db.ForeignKey('patient.id'))
    
    # qib_feature = db.relationship('QIBFeature',backref='modality')
    # patient  =  db.relationship('Patient',backref='modality')


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_stamp = db.Column(db.DateTime, default = datetime.now())
    sickness = db.Column(db.String(100))

    id_study= db.Column(db.Integer,  db.ForeignKey('study.id'))
    id_modality= db.Column(db.Integer,  db.ForeignKey('modality.id'))
    id_region= db.Column(db.Integer,  db.ForeignKey('region.id'))

    study = db.relationship('Study', backref='series')
    modality  =  db.relationship('Modality',backref='series') 
    region =  db.relationship('Region',backref='series') 

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))

    # id_qib_feature = db.Column(db.Integer, db.ForeignKey('qib_feature.id'))
    # id_patient= db.Column(db.Integer,  db.ForeignKey('patient.id'))
    
    # qib_feature = db.relationship('QIBFeature',backref='region')
    # patient  =  db.relationship('Patient',backref='region')

class Outcome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    outcome = db.Column(db.String(100))
    cancer = db.Column(db.Boolean)
    life_expectancy = db.Column(db.Integer)

    id_region = db.Column(db.Integer, db.ForeignKey('region.id'))
    region = db.relationship('Region', backref='outcome')

    id_patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship('Patient', backref='outcome')

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    id_family = db.Column(db.Integer, db.ForeignKey('family.id'))
    family = db.relationship('Family',backref='feature') #for schema

class QIB(db.Model):
    __tablename__ = 'qib'
    id = db.Column(db.Integer, primary_key=True)

    id_album = db.Column(db.Integer, db.ForeignKey('album.id'))
    time_stamp = db.Column(db.DateTime, default = datetime.now())

    album = db.relationship('Album',backref='qib')
    def __init__(self, id_album):
        self.id_album = id_album
        self.time_stamp = datetime.now()

class QIBFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feature_value = db.Column(db.Float)

    id_qib = db.Column(db.Integer, db.ForeignKey('qib.id'))
    id_feature = db.Column(db.Integer, db.ForeignKey(
        'feature.id'))
    id_series = db.Column(db.Integer, db.ForeignKey(
        'series.id'))
    
    feature = db.relationship('Feature', backref='qib_feature')
    qib = db.relationship('QIB',backref='qib_feature')
    series = db.relationship('Series',backref='qib_feature')

