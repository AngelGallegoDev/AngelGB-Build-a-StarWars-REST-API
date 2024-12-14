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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    all_character = [character.serialize() for character in characters]
    return jsonify(all_character)

@app.route('/character/<int:id>', methods=['GET'])
def get_one_characters(id):
    character = Character.query.filter_by( id= id).all()
    one_character = [character.serialize() for character in character]
    return jsonify(one_character)

@app.route('/characters', methods= ['POST'])
def add_character():
    body = request.get_json()
    if not body:
        return jsonify({"msg": "El cuerpo de la solicitud esta vacio"}), 400
    if 'name' not in body or 'height' not in body or 'mass' not in body or 'hair_color' not in body or 'skin_color' not in body or 'eye_color' not in body or 'birth_year' not in body or 'gender' not in body:
        return jsonify({"msg": "Completa los campos"}), 400
    new_character = Character(
        name=body['name'],
        height=body['height'],
        mass=body['mass'],
        hair_color=body['hair_color'],
        skin_color=body['skin_color'],
        eye_color=body['eye_color'],
        birth_year=body['birth_year'],
        gender=body['gender'],
        planet_id=body.get('planet_id')
        ) 

    db.session.add(new_character)
    db.session.commit()

    return jsonify(new_character.serialize()), 201   

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    all_planets = [planet.serialize() for planet in planets]
    return jsonify(all_planets)

@app.route('/planet/<int:id>', methods=['GET'])
def get_one_planet(id):
    planets = Planet.query.filter_by( id= id).all()
    one_planet = [planet.serialize() for planet in planets]
    return jsonify(one_planet)

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
