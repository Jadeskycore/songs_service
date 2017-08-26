import json
from unittest import TestCase

from bson import ObjectId

from app import app, mongo


class TestAverageDifficulty(TestCase):
    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            self.songs = mongo.db.songs
        self.song_ids = []

    def test_average_difficulty(self):
        payload1 = dict(
            artist='Despised Icon',
            title='Furtive Monologue',
            difficulty=10,
            level=100,
            released='2017-05-01'
        )
        response = self.app.put(
            '/songs/',
            data=payload1
        )

        self.song_ids.append(json.loads(response.get_data().decode())['_id'])

        payload2 = dict(
            artist='Despised Icon',
            title='In the arms of perdition',
            difficulty=20,
            level=100,
            released='2017-05-01'
        )
        response = self.app.put(
            '/songs/',
            data=payload2
        )

        self.song_ids.append(json.loads(response.get_data().decode())['_id'])

        response_avg_difficulty = self.app.get(
            '/songs/avg/difficulty',
            query_string={
                'level': 100
            }
        )

        average_difficulty = json.loads(
            response_avg_difficulty.get_data().decode()
        )['average_difficulty']

        assert average_difficulty == 15

    def tearDown(self):
        self.songs.delete_many({
            '_id': {
                '$in': list(map(ObjectId, self.song_ids))
            }
        })
