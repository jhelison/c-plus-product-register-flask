from flask import Flask
from flask_restful import Api

from resources.products import Products, ProductDetail
from resources.stock import Stock

app = Flask(__name__)
api = Api(app)


@app.route("/")
def home():
    return f"<h1>Backend Running...</h1>", 200


api.add_resource(Products, "/products/")
api.add_resource(ProductDetail, "/products/<id>")
api.add_resource(Stock, "/stock/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5151, threaded=True, debug=True)
