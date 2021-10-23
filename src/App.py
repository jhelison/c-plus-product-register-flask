from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
import os

from resources.products import Products, ProductDetail
from resources.stock import Stock
from resources.authentication import Authentication

from resources.user import User

database_path = os.path.abspath(os.getcwd()) + "\database.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["JWT_SECRET_KEY"] = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
api = Api(app)
jwt = JWTManager(app)


@app.route("/")
def home():
    return f"<h1>Backend Running...</h1>", 200


@app.before_first_request
def buildDatabase():
    db.create_all()


api.add_resource(Products, "/products/")
api.add_resource(ProductDetail, "/products/<id>")
api.add_resource(Stock, "/stock/")
api.add_resource(Authentication, "/auth/")

api.add_resource(User, "/users/", "/users/<id>", endpoint="users")


if __name__ == "__main__":
    from sql_alchemy import db

    db.init_app(app)
    app.run(host="0.0.0.0", port=5151, threaded=True, debug=True)
