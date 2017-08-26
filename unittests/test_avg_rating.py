import json
from unittest import TestCase

from bson import ObjectId

from app import app, mongo


class TestAverageRating(TestCase):
    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            self.songs = mongo.db.songs
        self.song_id = None

    def test_average_rating(self):

        payload = dict(
            artist='Despised Icon',
            title='Day of Mourning',
            difficulty=10,
            level=100,
            released='2017-05-01'
        )
        response = self.app.put(
            '/songs/',
            data=payload
        )

        self.song_id = json.loads(response.get_data().decode())['_id']

        # Add rating to song
        self.app.post(
            '/songs/rating',
            data={
                'song_id': self.song_id,
                'rating': 5
            }
        )

        self.app.post(
            '/songs/rating',
            data={
                'song_id': self.song_id,
                'rating': 5
            }
        )

        self.app.post(
            '/songs/rating',
            data={
                'song_id': self.song_id,
                'rating': 2
            }
        )
        # Get rating
        rating_response = self.app.get(
            f'/songs/avg/rating/{self.song_id}'
        )

        ratings = json.loads(rating_response.get_data().decode())

        assert ratings == {
                'average_rating': 4.0,
                'highest_rating': 5,
                'lowest_rating': 2
        }

    def tearDown(self):
        self.songs.delete_one({
            '_id': ObjectId(self.song_id)
        })
