from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt

from models.firebird.product import ProductStock
from models.sqlite.update import UpdateModel


class Stock(Resource):
    args = reqparse.RequestParser()
    args.add_argument("amount", type=float, required=False)

    def get(self):
        CODPROD = request.args.get("CODPROD")

        if not CODPROD:
            return 400

        try:
            stock = ProductStock.find_by_columns(CODPROD=CODPROD, CODEMPRESA=1)
            if not stock:
                return {"message": "Nenhum produto encontrado"}, 404

        except Exception as e:
            return {"message": "Erro ao pesquisar o produto", "error": str(e)}, 500

        return stock[0].json()

    @jwt_required()
    def patch(self):
        CODPROD = request.args.get("CODPROD")
        amount = Stock.args.parse_args()["amount"]

        user_id = get_jwt()["sub"]

        if not amount:
            return 400

        if not CODPROD:
            return 400

        try:
            stock = ProductStock.find_by_columns(CODPROD=CODPROD, CODEMPRESA=1)[0]
            if not stock:
                return {"message": "Nenhum produto encontrado"}, 404

            stock.ESTATU = float(stock.ESTATU) + amount
            stock.update()

            update = UpdateModel(user_id=user_id, product_code=CODPROD, quantity=amount)
            update.save_update()

        except Exception as e:
            print(e)
            return {"message": "Erro ao salvar o produto", "error": str(e)}, 500

        return stock.json()
