import datetime
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token

from models.sqlite.user import UserModel


class Authentication(Resource):
    args = reqparse.RequestParser()
    args.add_argument("phone_id", type=str, required=True)

    def post(self):
        phone_id = Authentication.args.parse_args()["phone_id"]

        user = UserModel.find_by_phone(phone_id)

        if not user:
            return {"message": "Usuario não encontrado"}, 404

        token = create_access_token(
            identity=user.id, expires_delta=datetime.timedelta(hours=12)
        )

        return {"token": token}, 200
