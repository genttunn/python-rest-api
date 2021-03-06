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

class OutcomeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'plc_status', 'id_patient')

class ModalitySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description')

class PatientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name','last_name', 'birthdate','gender', 'outcome')
    outcome = ma.Nested(OutcomeSchema)

class StudySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'time_stamp', 'patient')
    patient = ma.Nested(PatientSchema)
    
class QIBSchema(ma.Schema):
    class Meta:
        fields = ('id','time_stamp', 'album','name','description','outcome_column','metadata_columns')
    album = ma.Nested(AlbumSchema)

class SeriesSchema(ma.Schema):
    class Meta:
        fields = ('id','time_stamp','name','series_uid', 'sickness','modality','id_patient','patient')
    patient = ma.Nested(PatientSchema)
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



