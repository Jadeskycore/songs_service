from unittest import TestCase

from app import app, mongo


class TestCreateInvalidData(TestCase):
    def setUp(self):
        self.app = app.test_client()
        with app.app_context():
            self.songs = mongo.db.songs
        self.song_id = None

    def test_create_invalid_data(self):

        payload_wrong_difficulty = dict(
            artist='Despised Icon',
            title='Furtive Monologue',
            difficulty='Wrong string',
            level=1,
            released='2017-05-01'
        )
        response = self.app.put(
            '/songs/',
            data=payload_wrong_difficulty
        )

        assert response.status_code == 400

        payload_wrong_level = dict(
            artist='Despised Icon',
            title='Furtive Monologue',
            difficulty=1,
            level='Wrong string',
            released='2017-05-01'
        )

        response = self.app.put(
            '/songs/',
            data=payload_wrong_level
        )

        assert response.status_code == 400

        payload_wrong_date = dict(
            artist='Despised Icon',
            title='Furtive Monologue',
            difficulty=1,
            level=1,
            released='2017-05-0'
        )

        response = self.app.put(
            '/songs/',
            data=payload_wrong_date
        )

        assert response.status_code == 400
