from feature_manager.models import *

# def insert_family():
#     family_texture = Family(name='texture')
#     family_intensity = Family(name='intensity')
#     db.session.add(family)
#     db.session.commit()


def test_load():
    album = Album.query.filter_by(name='test_album_1').first()
    db.session.add(family)
    db.session.commit()