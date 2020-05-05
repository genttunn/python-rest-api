from app import db


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
    feature = db.relationship('Feature', backref='Feature1')
    qib = db.relationship('QIB', backref='QIB1')

    def __init__(self, id_qib, id_feature, value):
        self.idQIB = id_qib
        self.idFeature = id_feature
        self.featureValue = value
