from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    distance_from_earth = db.Column(db.Integer, nullable=False)
    nearest_star = db.Column(db.String, nullable=False)

    # Relationship
    missions = db.relationship('Mission', back_populates='planet', cascade='all, delete-orphan')
    
    # Serialization rules
    serialize_rules = ('-missions.planet',)

    def __repr__(self):
        return f'<Planet {self.name}>'

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)

    # Relationship
    missions = db.relationship('Mission', back_populates='scientist', cascade='all, delete-orphan')
    
    # Serialization rules
    serialize_rules = ('-missions.scientist',)

    @validates('name', 'field_of_study')
    def validate_scientist(self, key, value):
        if not value or not value.strip():
            raise ValueError(f'{key} cannot be empty.')
        return value.strip()

    def __repr__(self):
        return f'<Scientist {self.name}>'

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)

    # Relationships
    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')
    
    # Serialization rules
    serialize_rules = ('-scientist.missions', '-planet.missions')

    @validates('name', 'scientist_id', 'planet_id')
    def validate_mission(self, key, value):
        if key == 'name':
            if not value or not value.strip():
                raise ValueError('Mission name cannot be empty.')
            return value.strip()
        elif key in ['scientist_id', 'planet_id']:
            if not value:
                raise ValueError(f'{key} must be provided.')
            return value

    def __repr__(self):
        return f'<Mission {self.name}>'
