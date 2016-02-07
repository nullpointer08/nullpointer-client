import json
from ast import literal_eval
from display.media import Media
from settings import PLAYLIST_FILEPATH, SCHEDULE_TIME_STRING, SCHEDULE_URI_STRING, \
    SCHEDULE_TYPE_STRING, PLAYLIST_ID_STRING, PLAYLIST_MEDIA_URL_STRING, PLAYLIST_UPDATE_TIME_STRING, \
    SCHEDULE_NAME_STRING


def parse_playlist(pl_data):
    playlist_dl = json.loads(pl_data)
    playlist_id = playlist_dl[PLAYLIST_ID_STRING]
    playlist_update_time = playlist_dl[PLAYLIST_UPDATE_TIME_STRING]
    media_url = playlist_dl[PLAYLIST_MEDIA_URL_STRING]
    media_schedule = literal_eval(playlist_dl[SCHEDULE_NAME_STRING])
    media_schedule = generate_viewer_playlist(media_schedule)
    return media_url, media_schedule, playlist_id, playlist_update_time


def parse_playlist_json(pl_json):
    playlist = json.loads(pl_json)
    return generate_viewer_playlist(playlist)


def get_stored_playlist():
    with open(PLAYLIST_FILEPATH, 'r') as pl_file:
        playlist_json = pl_file.read()
    return parse_playlist_json(playlist_json)


def generate_viewer_playlist(playlist):
    viewer_pl = []
    for content in playlist:
        content_type = content[SCHEDULE_TYPE_STRING]
        content_uri = content[SCHEDULE_URI_STRING]
        view_time = int(content[SCHEDULE_TIME_STRING])
        media = Media(content_type, content_uri, view_time)
        viewer_pl.append(media)
    return viewer_pl


def save_playlist_to_file(playlist):
    json_playlist = []
    for content in playlist:
        json_content = {
            SCHEDULE_TYPE_STRING: content.content_type,
            SCHEDULE_URI_STRING: content.content_uri,
            SCHEDULE_TIME_STRING: content.view_time
        }
        json_playlist.append(json_content)
    with open(PLAYLIST_FILEPATH, 'w') as pl_file:
        pl_file.write(json.dumps(json_playlist))