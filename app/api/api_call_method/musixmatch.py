import requests
from app.views import Track
from app.api.api_call_method.coverpy_url import get_cover_img_url
from app.api.musix_api.lyrics_api import api_methods, base_url, format_url, api_key

track_collection = Track


def get_chart_data(page_num, page_size, country, has_lyric):
    method_choice = 0
    user_choice = api_methods[int(method_choice)]
    # start building the api call
    api_call = base_url + user_choice + format_url
    parameter_choice_string = "&page=" + str(page_num) + "&page_size=" + str(page_size) + "&country=" + str(
        country) + "&f_has_lyrics=" + str(
        has_lyric)
    api_call = api_call + parameter_choice_string
    api_call = api_call + api_key
    request = requests.get(api_call)
    data = request.json()
    return data


def fetch_data():
    data = get_chart_data(1, 100, "us", 1)['message']['body']['track_list']
    return data


def is_unique(track_name):
    number_of_track = track_collection.count_documents({"track_name": track_name})
    return number_of_track == 0


def insert_100_data():
    data = fetch_data()
    for track in data:
        # print(track)
        track = track['track']
        album_name = track['album_name']
        artist_name = track['artist_name']
        num_fav = track['num_favourite']
        track_name = track['track_name']
        url_img = get_cover_img_url(track_name)
        genres_size = len(track['primary_genres']['music_genre_list'])
        if genres_size > 0:
            genres = track['primary_genres']['music_genre_list'][0]['music_genre']['music_genre_name']
        else:
            genres = "NONE"
        insert_track = {
            "track_name": track_name,
            "artist_name": artist_name,
            "albums_name": album_name,
            "genre": genres,
            "num_favourite": num_fav,
            "url_img": url_img
        }
        if is_unique(str(track_name)):
            track_collection.insert_one(insert_track)
