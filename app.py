# https://chalice.readthedocs.io/en/latest/quickstart.html
from chalice import Chalice, CORSConfig, Response
from chalice import BadRequestError, NotFoundError
from urllib.parse import urlparse, parse_qs


app = Chalice(app_name='helloworld')
app.debug = True

# Some test objects
OBJECTS = {}
CITIES_TO_STATE = {
    'seattle': 'WA',
    'portland': 'OR',
}

# Example CORS configuration
cors_config = CORSConfig(
    allow_origin='*',
    allow_headers=['X-Special-Header'],
    max_age=600,
    expose_headers=['X-Special-Header'],
    allow_credentials=True
)

# Have to custom support multiple origins CORS
_ALLOWED_ORIGINS: set = {
    'http://allowed1.example.com',
    'http://allowed2.example.com',
}


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def index_post():
    # app.current_request.json_body is only available for the application/json content type, so we use raw_body
    parsed: dict = parse_qs(app.current_request.raw_body.decode())
    return {
        'states': parsed.get('states', [])
    }


@app.route('/custom_cors', methods=['GET'], cors=cors_config)
def supports_custom_cors():
    return {'cors': True}


@app.route('/cors_multiple_origins', methods=['GET'])
def supports_cors_multiple_origins():
    origin = app.current_request.to_dict()['headers'].get('origin', '')
    if origin in _ALLOWED_ORIGINS:
        return Response(
            body='You sent a whitelisted origin!\n',
            headers={
                'Access-Control-Allow-Origin': origin
            })
    else:
        return "The origin you sent has not been whitelisted: %s\n" % origin


@app.route('/introspect')
def introspect():
    return app.current_request.to_dict()


@app.route('/cities/{city}')
def state_of_city(city: str):
    try:
        return {'state': CITIES_TO_STATE[city]}
    except KeyError:
        raise BadRequestError(
            f'Unknown city \'{city.title()}\', '
            f'valid choices are : {", ".join([c.title() for c in CITIES_TO_STATE.keys()])}'
        )


@app.route('/resource/{value}', methods=['PUT'])
def put_test(value: any):
    return {"value": value}


@app.route('/objects/{key}', methods=['GET', 'PUT'])
def my_object(key: str):
    request = app.current_request

    if request.method == 'PUT':
        OBJECTS[key] = request.json_body
    elif request.method == 'GET':
        try:
            return {key: OBJECTS[key]}
        except KeyError:
            raise NotFoundError(key)
