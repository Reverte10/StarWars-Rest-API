"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ----endpoints---- :

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/characters', methods=['GET'])
def get_characters():
    characters_query = Character.query.all()
    results = list(map(lambda item: item.serialize(), characters_query))
    response_body = {
        "msg": "OK", 
        "results": results
    }

    return jsonify(response_body), 200


@app.route('/characters/<int:characters_id>', methods=['GET'])
def get_one_characters(characters_id):
    character_query = Character.query.filter_by(id=characters_id).first()

    response_body = {
        "msg": "OK", 
        "results": character_query.serialize()
    }

    return jsonify(response_body), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets_query = Planet.query.all()
    results = list(map(lambda item: item.serialize(), planets_query))
    response_body = {
        "msg": "OK", 
        "results": results
    }

    return jsonify(response_body), 200


@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_one_planets(planets_id):
    planet_query = Planet.query.filter_by(id=planets_id).first()

    response_body = {
        "msg": "OK", 
        "results": planet_query.serialize()
    }

    return jsonify(response_body), 200


@app.route('/users', methods=['GET'])
def get_all_users():

    users_query = User.query.all()
    results = list(map(lambda item: item.serialize(), users_query))

    response_body = {
       "results": results
    }

    return jsonify(response_body), 200


@app.route('/users/<int:user_id>/favoritos', methods=['GET'])
def get_favoritos(user_id):

    favorito_query = Favorite.query.filter_by(id=user_id).first()
    
    response_body = {
       "results": favorito_query.serialize()
    }

    return jsonify(response_body), 200


@app.route('/users/<int:user_id>/favoritos/', methods=['POST'])
def add_favorito(user_id):

    request_body = request.get_json(force=True)

    favorito = Favorite(characters_id= request_body['characters_id'],
                        planets_id= request_body['planets_id'],
                        user_id= user_id)

    db.session.add(favorito)
    db.session.commit()

    response_body = {
        'msg':'ok',
        "results": ['Favorito Created', favorito.serialize()]
    }

    return jsonify(response_body), 200


@app.route('/users', methods=['POST'])
def create_user():

    request_body = request.get_json(force=True)

    user = User(email=request_body['email'],
                password=request_body['password'],
                is_active=request_body['is_active'])
    
    db.session.add(user)
    db.session.commit()


    response_body = {
       "results": 'User Created'
    }
    return jsonify(response_body), 200


@app.route('/users/<int:user_id>/favoritos/', methods=['DELETE'])
def del_favorito(user_id ):

    body = request.get_json(force=True)
    
    if body["characters_id"] is None:
        favorito_query= Favorite.query.filter_by(user_id=user_id).filter_by(planets_id=body["planets_id"]).first()
    
    else:
        favorito_query= Favorite.query.filter_by(user_id=user_id).filter_by(characters_id=body["characters_id"]).first()
   
    db.session.delete(favorito_query)
    db.session.commit()

    response_body = {
        'msg':'ok',
        "results": 'Favorito deleted'
    }

    return jsonify(response_body), 200


# ----fin endpoints---- :
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
