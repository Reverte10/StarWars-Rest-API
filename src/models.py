from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

#creación de nuevas tablas:
class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    birth_year = db.Column(db.Integer)
    gender = db.Column(db.String(250))
    height = db.Column(db.Integer)
    skin_color = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))
    # favorites = db.relationship ('favorites', backref='characters', lazy = True)

    def __repr__(self):
        return '<Characters %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            # "favorites": self.favorites
        }
    
class Planet(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    climate = db.Column(db.String(250))
    population = db.Column(db.Integer)
    orbital_period = db.Column(db.Integer)
    rotation_period = db.Column(db.Integer)
    diameter = db.Column(db.Integer)
    # favorites = db.relationship ('favorites', backref='planets', lazy = True)

    def __repr__(self):
        return '<Planets %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
            "orbital_period": self.orbital_period,
            "rotation_period": self.rotation_period,
            "diameter": self.diameter,
            # "favorites": self.favorites
        }
    
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey ('user.id'), nullable=False)
    characters_id = db.Column(db.Integer, db.ForeignKey ('characters.id'), nullable=True)
    planets_id = db.Column(db.Integer, db.ForeignKey ('planets.id'), nullable=True)

    def __repr__(self):
        return '<Favorite %r>' % self.id

def serialize(self):
        character_query= Character.query.filter_by(id= self.characters_id).first()

        if character_query is None:
          character_resultado=  None
        else:
          character_resultado= character_query.serialize()['name']

        planet_query= Planet.query.filter_by(id= self.planets_id).first()

        if planet_query is None:
          planet_resultado=  None
        else:
          planet_resultado= planet_query.serialize()['name']
        

        return {
            "id": self.id,
            "characters": character_resultado,
            "planets": planet_resultado,
            "user_id": self.user_id
            # do not serialize the password, its a security breach // planet_query.serialize()['name'] // character_query.serialize()['name']
        }