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
from models import db, User, Character, Planet, Favorito
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import re
#from models import Person

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

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

# --- ENDPOINTS ---

# ----------------------- GET -----------------------

# CHARACTERS

@app.route('/characters', methods=['GET'])
def get_all_characters():

    characters_query = Character.query.all()
    results = list(map(lambda item: item.serialize(), characters_query))

    response_body = {
       "results": results
    }

    return jsonify(response_body), 200


@app.route('/characters/<int:character_id>', methods=['GET'])
def get_one_characters(character_id):

    character_query = Character.query.filter_by(id=character_id).first()
    
    if character_query is None:
        return jsonify({"msg": "Character not exist"}), 404

    response_body = {
       "results": character_query.serialize()
    }

    return jsonify(response_body), 200

# PLANETS

@app.route('/planets', methods=['GET'])
def get_all_planets():

    planets_query = Planet.query.all()
    results = list(map(lambda item: item.serialize(), planets_query))

    response_body = {
       "results": results
    }

    return jsonify(response_body), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planets(planet_id):

    planet_query = Planet.query.filter_by(id=planet_id).first()

    if planet_query is None:
        return jsonify({"msg": "Planet not exist"}), 404

    response_body = {
       "results": planet_query.serialize()
    }

    return jsonify(response_body), 200

# USERS

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

    # UN FAVORITO

    favorito_query = Favorito.query.filter_by(user_id=user_id).first()

    response_body = {
       "results": favorito_query.serialize()
    }

    return jsonify(response_body), 200


# ----------------------- POST -----------------------
# FAVORITOS 

@app.route('/users/<int:user_id>/favoritos/', methods=['POST'])
def add_favorito(user_id):

    request_body = request.get_json(force=True)

    favorito = Favorito(characters_id= request_body['characters_id'],
                        planets_id= request_body['planets_id'],
                        user_id= user_id)
    
    db.session.add(favorito)
    db.session.commit()

    response_body = {
        'msg':'ok',
        "results": ['Favorito Created', favorito.serialize()]
    }

    return jsonify(response_body), 200


# USERS

@app.route('/users', methods=['POST'])
def create_user():

    request_body = request.get_json(force=True)

    user = User(email=request_body['email'],
                password=request_body['password'],
                is_active=request_body['is_active'])
    
    if request_body['email'] is None or request_body['password'] is None or request_body['is_active'] is None:
        return jsonify ({
            'msg':'missing parameters (email, password, is_active are required)'
        }), 400
    
    # Verificamos email válido (basic)

    # if "@" not in request_body['email'] or "." not in request_body['email']:
    #     return jsonify ({
    #         'msg':'wrong email format(check @ .)'
    #     }), 400

    # Verificamos email válido (pro)

    def validar_email(email):
    # Patrón de expresión regular para validar el email
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Usamos re.match() para verificar el patrón en el email proporcionado
        if re.match(patron_email, email):
            return True
        else:
            return False

    if validar_email(request_body['email']):
        print("El email es válido.")
    else:
        return jsonify ({
            'msg':'wrong email format(check @ .)'
        }), 400

    db.session.add(user)
    db.session.commit()

    response_body = {
       "results": 'User Created'
    }

    return jsonify(response_body), 200

# ----------------------- DELETE -----------------------

@app.route('/users/<int:user_id>/favoritos/', methods=['DELETE'])
def del_favorito(user_id ):

    body = request.get_json(force=True)
    
    if body["characters_id"] is None:
        favorito_query= Favorito.query.filter_by(user_id=user_id).filter_by(planets_id=body["planets_id"]).first()
    
    else:
        favorito_query= Favorito.query.filter_by(user_id=user_id).filter_by(characters_id=body["characters_id"]).first()
   

    db.session.delete(favorito_query)
    db.session.commit()

    response_body = {
        'msg':'ok',
        "results": 'Favorito deleted'
    }

    return jsonify(response_body), 200

# ----------------------- PUT -----------------------

@app.route('/users/<int:user_id>', methods=['PUT', 'GET'])
def get_single_user(user_id):

    body = request.get_json(force=True) #{ 'username': 'new_username'}
    if request.method == 'PUT':
        user1 = User.query.get(user_id)
        user1.email = body["email"]
        db.session.commit()
        return jsonify(user1.serialize()), 200
    if request.method == 'GET':
        user1 = User.query.get(user_id)
        return jsonify(user1.serialize()), 200

    return "Invalid Method", 404


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"msg": "email do not exist"}), 404

    if password != user.password:
        return jsonify({"msg": "Bad password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    if user is None:
        return jsonify({"msg": "user do not exist"}), 404
    return jsonify(logged_in_as=current_user), 200

# --- FIN ENDPOINTS ---

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)