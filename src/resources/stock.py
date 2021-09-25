from flask import request
from flask_restful import Resource

from models.product import ProductStock


class Stock(Resource):
    def get(self):
        CODPROD = request.args.get("CODPROD")

        try:
            if CODPROD:
                stock = ProductStock.find_by_columns(CODPROD=CODPROD, CODEMPRESA=1)
                if not stock:
                    return {"message": "Nenhum produto encontrado"}, 404

            else:
                return 404

        except Exception as e:
            return {"message": "Erro ao pesquisar o produto", "error": str(e)}, 500

        return stock[0].json()
