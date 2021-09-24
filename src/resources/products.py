from flask import request
from flask_restful import Resource

from models.product import ProductModel


class Products(Resource):
    def get(self):
        query = request.args.get("query")
        # ?query=product%20name

        try:
            if query:
                products = ProductModel.find_by_columns(
                    NOMEPROD=query, exact=False, page=1, limit=50
                )
            else:
                products = ProductModel.all(page=1, limit=50)
        except Exception as e:
            return {"message": "Erro ao pesquisar o produto", "error": str(e)}, 500

        return [product.json() for product in products]
