from feature_manager.models import *

def insert_family():
    family = Family(name='texture')
    db.session.add(family)
    db.session.commit()