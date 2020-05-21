from feature_manager.models import *

def test_insert():
    family = Family(name='test')
    db.session.add(family)
    db.session.commit()