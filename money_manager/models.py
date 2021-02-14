from app import db
DB = db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String())
    sheet_id = db.Column(db.String())

    def __init__(self, google_id, sheet_id):
        self.google_id = google_id
        self.sheet_id = sheet_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'google_id': self.google_id,
            'sheet_id': self.sheet_id
        }