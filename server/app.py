#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return [{"id": s.id, "name": s.name, "field_of_study": s.field_of_study} for s in scientists]

    def post(self):
        data = request.get_json()
        try:
            new_scientist = Scientist(name=data['name'], field_of_study=data['field_of_study'])
            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(), 201
        except ValueError as e:
            return {"errors": [str(e)]}, 400

class ScientistsById(Resource):
    def get(self, id):
        scientist = Scientist.query.get(id)
        if scientist:
            return scientist.to_dict(rules=('-missions.scientist',)), 200
        return {"error": "Scientist not found"}, 404

    def patch(self, id):
        scientist = Scientist.query.get(id)
        if not scientist:
            return {"error": "Scientist not found"}, 404

        data = request.get_json()
        try:
            for attr in data:
                setattr(scientist, attr, data[attr])
            db.session.commit()
            return scientist.to_dict(), 202
        except ValueError as e:
            return {"errors": [str(e)]}, 400

    def delete(self, id):
        scientist = Scientist.query.get(id)
        if not scientist:
            return {"error": "Scientist not found"}, 404

        db.session.delete(scientist)
        db.session.commit()
        return "", 204

class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        return [{"id": p.id, "name": p.name, "distance_from_earth": p.distance_from_earth, "nearest_star": p.nearest_star} for p in planets]

class Missions(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_mission = Mission(name=data['name'], scientist_id=data['scientist_id'], planet_id=data['planet_id'])
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(rules=('-scientist.missions', '-planet.missions')), 201
        except ValueError as e:
            return {"errors": [str(e)]}, 400

api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistsById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
