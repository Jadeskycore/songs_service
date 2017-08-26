import datetime
import os
import re

from werkzeug.exceptions import BadRequest, NotFound

from bson import ObjectId
from bson.errors import InvalidId
from fields import (add_song_fields, difficulty_fields, rating_set_fields,
                    search_fields, songs_fields)
from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_restplus import Api, Resource, fields

app = Flask(__name__)

app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.config['ERROR_404_HELP'] = False

mongo = PyMongo(app)
api = Api(app)


get_songs_model = api.model('GetSongs', {
    '_id': fields.String,
    'artist': fields.String,
    'title': fields.String,
    'difficulty': fields.Integer,
    'level': fields.Integer,
    'released': fields.DateTime
})

get_avg_model = api.model('Response', {
    'average_rating': fields.Float,
    'highest_rating': fields.Integer,
    'lowest_rating': fields.Integer,
})


@api.route(
    '/songs/',
)
class Songs(Resource):
    @api.expect(songs_fields, validate=True)
    @api.response(200, 'Success', get_songs_model)
    def get(self):
        args = songs_fields.parse_args()
        offset = args.get('offset')

        songs_query = mongo.db.songs.find()

        if offset:
            songs_query.skip(offset).limit(10)

        return jsonify([
            {
                k: (v if k != '_id' else str(v)) for k, v in song.items()
            }
            for song in songs_query
        ])

    @api.expect(add_song_fields, validate=True)
    @api.response(201, 'Created')
    @api.response(400, 'Bad request')
    def put(self):
        args = add_song_fields.parse_args()
        songs_collection = mongo.db.songs
        data = {
            k: (str(v) if isinstance(v, datetime.date) else v)
            for k, v in args.items()
        }
        new_song_id = songs_collection.insert_one(data).inserted_id
        return jsonify({
            '_id': str(new_song_id)
        })


@api.route(
    '/songs/avg/difficulty',
)
class SongGetAverageDifficulty(Resource):
    @api.expect(difficulty_fields, validate=True)
    @api.response(200, 'Success')
    def get(self):
        args = difficulty_fields.parse_args()
        level = args.get('level')

        songs_collection = mongo.db.songs

        if level:
            songs_query = songs_collection.find({
                'level': level
            })
        else:
            songs_query = songs_collection.find()

        songs = [
            item_map["difficulty"] for item_map in songs_query
        ]

        if not songs:
            return jsonify({
                'message': 'No songs for this level'
            })

        return jsonify({
            'average_difficulty': sum(songs)/len(songs)
        })


@api.route(
    '/songs/search',
)
class SongSearch(Resource):
    @api.expect(search_fields, validate=True)
    @api.response(200, 'Success', get_songs_model)
    def get(self):
        args = search_fields.parse_args()
        message = args.get('message')

        songs_collection = mongo.db.songs

        # ignore case in this regex
        pattern = re.compile(r'{}'.format(message.strip()), re.I)

        # search both in title and artist
        songs = [item for item in songs_collection.find(
            {"$or": [
                {"title": pattern},
                {"artist": pattern}
            ]}
        )]

        return jsonify([
            {
                k: (v if k != '_id' else str(v)) for k, v in song.items()
            }
            for song in songs
        ])


@api.route(
    '/songs/rating',
)
class SongSetRating(Resource):
    @api.expect(rating_set_fields, validate=True)
    @api.response(404, 'Not Found')
    @api.response(400, 'Bad request')
    @api.response(201, 'Created')
    def post(self):
        data = rating_set_fields.parse_args()

        song_id = data.get('song_id')
        rating = data.get('rating')

        if not 1 <= rating <= 5:
            raise BadRequest('Rating should be between [1, 5]')

        songs_collection = mongo.db.songs
        try:
            song_obj_id = ObjectId(song_id)
        except InvalidId:
            raise BadRequest('Wrong `song_id` format')

        if songs_collection.find({'_id': song_obj_id}).count() == 0:
            raise NotFound('Song not found')

        songs_collection.update_one({
            '_id': song_obj_id
        }, {
            '$push': {
                'rating': rating
            }
        })

        return None, 201


@api.route(
    '/songs/avg/rating/<string:song_id>',
)
class SongGetAverageRating(Resource):
    @api.response(404, 'Not Found')
    @api.response(400, 'Bad request')
    @api.response(200, 'Success', get_avg_model)
    def get(self, song_id):

        songs_collection = mongo.db.songs

        try:
            song_obj_id = ObjectId(song_id)
        except InvalidId:
            raise BadRequest('Wrong `song_id` format')

        song = songs_collection.find_one({'_id': song_obj_id})

        if not song:
            raise NotFound('Song not found')

        song_rating = song.get('rating')

        if not song_rating:
            data = {
                'message': 'Nobody rated this song yet'
            }
        else:
            data = {
                'average_rating': sum(song_rating)/len(song_rating),
                'highest_rating': max(song_rating),
                'lowest_rating': min(song_rating)
            }

        return jsonify(data)


if __name__ == '__main__':
    app.run()
