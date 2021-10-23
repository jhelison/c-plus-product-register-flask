from flask import request
from flask_restful import Resource

from models.firebird.product import ProductModel


class Products(Resource):
    def get(self):
        NOMEPROD = request.args.get("NOMEPROD")
        PAGE = request.args.get("PAGE")

        try:
            PAGE = int(PAGE)
        except:
            PAGE = 1

        try:
            if NOMEPROD:
                products = ProductModel.find_by_columns(
                    NOMEPROD=NOMEPROD, exact=False, page=PAGE, limit=50
                )
            else:
                products = ProductModel.all(page=PAGE, limit=50)
        except Exception as e:
            return {"message": "Erro ao pesquisar o produto", "error": str(e)}, 500

        return [product.json() for product in products]


class ProductDetail(Resource):
    def get(self, id):

        try:
            product = ProductModel.find_by_key(id)

            if not product:
                return {"message": "Produto não encontrado"}, 404

        except Exception as e:
            return {"message": "Erro ao pesquisar o produto", "error": str(e)}, 500

        return product.json()
