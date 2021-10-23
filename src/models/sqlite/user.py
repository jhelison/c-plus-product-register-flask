from sql_alchemy import db
from datetime import datetime


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @classmethod
    def find_user(cls, id):
        user = cls.query.filter_by(id=id).first()
        if user:
            return user
        return None

    @classmethod
    def find_by_phone(cls, phone_id):
        user = cls.query.filter_by(phone_id=phone_id).first()
        if user:
            return user
        return None

    def as_dict(self):
        return {
            "id": self.id,
            "phone_id": self.phone_id,
            "name": self.name,
            "created_at": str(self.created_at),
        }

    def save_user(self):
        db.session.add(self)
        db.session.commit()
