from flask import Flask, jsonify, request, make_response, abort
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
    print(product)
    answer = parser_obj.get_blocks(product.get('name'))
    print(product)
    return "load\n", 201


if __name__ == '__main__':
    app.run(debug=True)
