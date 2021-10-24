from sql_alchemy import db
from datetime import datetime

from models.sqlite.user import UserModel


class UpdateModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_code = db.Column(db.String(18), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    quantity = db.Column(db.Integer, nullable=False)

    @classmethod
    def find_by_product_code(cls, product_code):
        updates = cls.query.filter_by(product_code=product_code)
        return updates

    def as_dict(self):
        user = UserModel.find_user(self.user_id)

        return {
            "id": self.id,
            "user": user.as_dict(),
            "product_code": self.product_code,
            "created_at": str(self.created_at),
            "quantity": self.quantity,
        }

    def save_update(self):
        db.session.add(self)
        db.session.commit()
