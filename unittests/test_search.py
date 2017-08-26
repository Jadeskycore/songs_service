import json
from unittest import TestCase

from app import app, mongo
from bson import ObjectId


class TestSearch(TestCase):
    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            self.songs = mongo.db.songs
        self.song_id = None

    def test_search(self):

        payload = dict(
            artist='Despised Icon',
            title='Furtive Monologue',
            difficulty=10,
            level=1,
            released='2017-05-01'
        )
        response = self.app.put(
            '/songs/',
            data=payload
        )

        self.song_id = json.loads(response.get_data().decode())['_id']

        # Test case sensitivity
        response_search = self.app.get(
            '/songs/search',
            query_string={
                'message': 'Despised'
            }
        )
        expected_song_data = payload.copy()
        expected_song_data['_id'] = self.song_id
        matched_songs = json.loads(response_search.get_data().decode())

        assert expected_song_data == matched_songs[0]

        # Test case insensitivity
        response_search = self.app.get(
            '/songs/search',
            query_string={
                'message': 'dESpIsEd'
            }
        )

        matched_songs = json.loads(response_search.get_data().decode())
        assert expected_song_data == matched_songs[0]

        response_search = self.app.get(
            '/songs/search',
            query_string={
                'message': 'Monologue'
            }
        )

        matched_songs = json.loads(response_search.get_data().decode())
        assert expected_song_data == matched_songs[0]

    def tearDown(self):
        self.songs.delete_one({
            '_id': ObjectId(self.song_id)
        })

        self.songs.delete_many({
            'artist': 'Despised Icon'
        })
