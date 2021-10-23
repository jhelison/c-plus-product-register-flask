from flask import request
from flask_restful import Resource, reqparse

from models.sqlite.update import UpdateModel


class Update(Resource):
    def get(self, id):
        if not id:
            return 400

        try:
            updates = UpdateModel.find_by_product_code(product_code=id)
            updates_json = [update.as_dict() for update in updates]
        except Exception as e:
            return {"message": "Erro ao pesquisar o produto", "error": str(e)}, 500

        return updates_json
