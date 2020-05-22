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

class RegionSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description')

class ModalitySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description')

class PatientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name','last_name', 'birthdate','gender')

class StudySchema(ma.Schema):
    class Meta:
        fields = ('id','name', 'id_patient','patient', 'time_stamp')
    patient = ma.Nested(PatientSchema)

class QIBSchema(ma.Schema):
    class Meta:
        fields = ('id','time_stamp', 'album')
    album = ma.Nested(AlbumSchema)

class SeriesSchema(ma.Schema):
    class Meta:
        fields = ('id','time_stamp', 'sickness','study','modality')
    study = ma.Nested(StudySchema)
    modality = ma.Nested(ModalitySchema)

class SeriesRegionSchema(ma.Schema):
    class Meta:
        fields = ('id_series', 'region')
    region = ma.Nested(RegionSchema)

class QIBFeatureSchema(ma.Schema):
    class Meta:
        fields = ('id', 'feature_value', 'feature', 'qib','series_region')
    feature = ma.Nested(FeatureSchema)
    qib = ma.Nested(QIBSchema)
    series_region = ma.Nested(SeriesRegionSchema)





class AlbumSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name','description', 'time_stamp')

class StudyAlbumSchema(ma.Schema):
    class Meta:
        fields = ('id_study', 'id_album')

