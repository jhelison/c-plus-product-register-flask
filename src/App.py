from flask import Flask
from flask_restful import Api

from resources.products import Products

app = Flask(__name__)
api = Api(app)


@app.route("/")
def home():
    return f"<h1>Backend Running...</h1>", 200


api.add_resource(Products, "/products/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5151, threaded=True, debug=True)
