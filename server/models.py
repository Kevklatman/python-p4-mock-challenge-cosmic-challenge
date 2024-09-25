from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship("Mission", back_populates="planet")
    # Add serialization rules
    serialize_rules = ('-missions.planet',)

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=True)  # Change this to True

    # Add relationship
    missions = db.relationship("Mission", back_populates="scientist")
    # Add serialization rules
    serialize_rules = ('-missions.scientist',)
    serialize_only = ('id', 'name', 'field_of_study')
    # Add validation

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Scientist name cannot be empty idiot")
        return name
    
    @validates('field_of_study')
    def validate_field(self, key, field_of_study):
        if field_of_study is not None and not field_of_study.strip():
            raise ValueError("Field of study cannot be empty stupid")
        return field_of_study
    
def __repr__(self):
    return f"<Scientist {self.name}, {self.field_of_study}>"


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # Add relationships
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable = False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable = False)

    planet = db.relationship("Planet", back_populates="missions")
    scientist = db.relationship("Scientist", back_populates="missions")

    # Add serialization rules
    serialize_rules = ('-planet.missions', '-scientist.missions')
    # Add validation

    @validates('name')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Mission name cannot be empty")
        return name.strip()

    @validates('scientist_id', 'planet_id')
    def validate_foreign_keys(self, key, value):
        if value is None:
            raise ValueError(f"{key.replace('_id', '').capitalize()} must be assigned to the mission")
        return value
# add any models you may need.
