from flask import request, jsonify
from flask_restful import Resource, reqparse
from sql_alchemy import db

from models.sqlite.user import UserModel


class User(Resource):
    args = reqparse.RequestParser()
    args.add_argument("phone_id", type=str, required=True)
    args.add_argument("name", type=str, required=True)

    def get(self, id):
        user = UserModel.find_user(id)

        if not user:
            return {"message": "Usuario não encontrado"}, 404

        return jsonify(user.as_dict())

    def put(self, id=None):
        args = User.args.parse_args()

        if UserModel.find_by_phone(args["phone_id"]):
            return {"message": "Usuario já existente"}, 400

        user = UserModel(**args)
        user.save_user()

        return jsonify(user.as_dict())
