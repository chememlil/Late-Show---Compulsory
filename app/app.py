#!/usr/bin/env python3

from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
from marshmallow import fields, post_dump

from models import db, Episodes, Appearances, Guests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)
ma = Marshmallow(app)

@app.route('/')
def home():
    return "Welcome to the Flask app!"

class GuestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Guests
        exclude = ['created_at','updated_at']

    id = ma.auto_field()
    name = ma.auto_field()
    occupation = ma.auto_field()

class EpisodesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Episodes
        exclude = ['created_at', 'updated_at']
    
    id = ma.auto_field()
    date = ma.auto_field()
    number = ma.auto_field()
    guests = fields.List(fields.Nested('GuestSchema'))

    @post_dump(pass_many=True)
    def remove_fields(self, data, many):
        if many:
            print(data)
            for x in data:
                x.pop('guests')
            return data
        
        return data
    
class AppearanceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Appearances
        exclude = ['created_at', 'updated_at']

    id = ma.auto_field()
    rating = ma.auto_field()
    episode = fields.Nested('EpisodesSchema')
    guest = fields.Nested('GuestSchema')

    @post_dump(pass_many=True)
    def filter_fields(self, data, many):
        if not many:
            print(data)
            data['episode'].pop('guests')
            return data
        return data

    

class Episodess(Resource):
    def get(self):
        episodes_schema = EpisodesSchema(many=True)
        episodes = Episodes.query.all()
        episodes_dict = episodes_schema.dump(episodes)
        return make_response(jsonify(episodes_dict), 200)
    

class EpisodeById(Resource):
    def get(self,id):
        episode_schema = EpisodesSchema()
        episode = Episodes.query.filter_by(id=id).first()

        if episode:
            response = episode_schema.dump(episode)
            return make_response(jsonify(response), 200)
        
        return make_response(jsonify({'error': "Episode not found"}), 404)
    
    def delete(self, id):
        episode = Episodes.query.filter_by(id=id).first()

        if episode:
            db.session.delete(episode)
            db.session.commit()

            return make_response({}, 204)
        
        return {'error': 'Episode not found'}, 404
    

class Guestss(Resource):
    def get(self):
        guest_schema = GuestSchema(many=True)
        guests = Guests.query.all()
        guests_dict = guest_schema.dump(guests)

        return make_response(jsonify(guests_dict), 200)
    
class Appearancess(Resource):
    def post(self):
        data = request.get_json()

        appearance = Appearances(
            rating = data.get('rating'),
            episode_id = data.get('episode_id'),
            guest_id = data.get('guest_id')
        )

        db.session.add(appearance)
        db.session.commit()

        if appearance.id:
            appearance_schema = AppearanceSchema()
            respose = make_response(jsonify(appearance_schema.dump(appearance)), 201)
            return respose
        return {'errors': ['Validation errors']}


api.add_resource(Episodess, '/episodes')
api.add_resource(EpisodeById, '/episodes/<int:id>')
api.add_resource(Guestss, '/guests')
api.add_resource(Appearancess, '/appearances')



if __name__ == '__main__':
    app.run(port=5555)
