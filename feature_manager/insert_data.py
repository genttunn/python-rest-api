from feature_manager import models,db

# def insert_family():
#     family_texture = Family(name='texture')
#     family_intensity = Family(name='intensity')
#     db.session.add(family)
#     db.session.commit()


def test_load():
    album = models.Album.query.filter_by(name='test_album_1').first()
    db.session.add(album)
    db.session.commit()