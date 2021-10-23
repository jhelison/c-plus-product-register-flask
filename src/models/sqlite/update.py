from sql_alchemy import db
from datetime import datetime


class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_code = db.Column(db.String(18), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
