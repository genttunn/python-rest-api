from feature_manager import ma

class FamilySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

class FeatureSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name','family')
    family = ma.Nested(FamilySchema)

class AlbumSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'time_stamp')

class QIBSchema(ma.Schema):
    class Meta:
        fields = ('id','time_stamp', 'album')
    album = ma.Nested(AlbumSchema)

class QIBFeatureSchema(ma.Schema):
    class Meta:
        fields = ('id', 'feature_value', 'feature', 'qib')
    feature = ma.Nested(FeatureSchema)
    qib = ma.Nested(QIBSchema)

class PatientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name','last_name', 'birthdate','gender')

class StudySchema(ma.Schema):
    class Meta:
        fields = ('id', 'patient', 'time_stamp')
    patient = ma.Nested(PatientSchema)

class AlbumSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name','description', 'time_stamp')

class StudyAlbumSchema(ma.Schema):
    class Meta:
        fields = ('id_study', 'id_album')