from feature_manager import app, jsonify,request
from feature_manager.models import *
from feature_manager.schemas import *
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