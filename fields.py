from datetime import datetime

from flask_restplus import reqparse

songs_fields = reqparse.RequestParser()
songs_fields.add_argument('offset', type=int, location="args", required=False)

add_song_fields = reqparse.RequestParser()
add_song_fields.add_argument('artist', type=str, location='form', required=True)
add_song_fields.add_argument('title', type=str, location='form', required=True)
add_song_fields.add_argument('difficulty', type=int, location='form', required=True)
add_song_fields.add_argument('level', type=int, location='form', required=True)
add_song_fields.add_argument(
    'released',
    type=lambda x: datetime.strptime(x, '%Y-%m-%d').date(),
    location='form',
    required=True
)

difficulty_fields = reqparse.RequestParser()
difficulty_fields.add_argument('level', type=int, location='args', required=False)

search_fields = reqparse.RequestParser()
search_fields.add_argument('message', type=str, location='args', required=True)

rating_set_fields = reqparse.RequestParser()
rating_set_fields.add_argument('song_id', type=str, location='form', required=True)
rating_set_fields.add_argument('rating', type=int, location='form', required=True)
