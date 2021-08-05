import json
import requests
from flask import Flask, request, make_response, abort
from src.parserAvito import AvitoParser

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(error, 404)


@app.route('/', methods=['POST'])
def read_request():
    if not request.json or not 'search' in request.json:
        abort(400)
    product = {
        'name': request.json['search'],
    }
    try:
        product['callback'] = request.json['callback']
    except (ValueError, KeyError, TypeError):
        product['callback'] = request.remote_addr
    parser_obj = AvitoParser()
    objects = parser_obj.parse(product.get('name'))
    print(objects)
    my_json = {
        "search": product.get('name'),
        "result": [x.to_json() for x in objects]}
    # print(my_json["result"])
    if product['callback'] is not request.remote_addr:
        r = requests.get(product['callback'], params=json.dumps(my_json))
        return r.status_code, 201
    return json.dumps(my_json), 201


if __name__ == '__main__':
    app.run()
