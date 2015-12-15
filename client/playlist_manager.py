import logging
import requests
import json
import os

from ast import literal_eval
from display.media import Media
from downloader import ChunkedDownloader
from downloader import ResumableFileDownload


class PlaylistManager(object):

    LOG = logging.getLogger(__name__)
    SCHEDULE_NAME_STRING = 'media_schedule_json'
    SCHEDULE_TIME_STRING = 'time'
    SCHEDULE_TYPE_STRING = 'type'
    SCHEDULE_URI_STRING = 'uri'

    def __init__(self, config):
        # Device ID
        device_id_file = open(config.get('Device', 'device_id_file'), 'r')
        self.DEVICE_ID = device_id_file.read().strip()
        device_id_file.close()

        # Playlist URL
        incomplete_url = config.get('Server', 'playlist_url')
        self.PLAYLIST_URL = incomplete_url.format(**{'device_id': self.DEVICE_ID})

        # Playlist file
        playlist_file = config.get('Storage', 'playlist_file')
        playlist_folder = os.path.dirname(playlist_file)
        if not os.path.exists(playlist_folder):
            os.makedirs(playlist_folder)
        self.PLAYLIST_FILEPATH = playlist_file

        # Media folder
        self.MEDIA_FOLDER = config.get('Storage', 'media_folder')
        if not os.path.exists(self.MEDIA_FOLDER):
            os.makedirs(self.MEDIA_FOLDER)

        # Create empty playlist
        self.playlist = []

        # Utility for downloading files
        self.downloader = ChunkedDownloader(self.PLAYLIST_URL, self.DEVICE_ID)

    def fetch_remote_playlist_data(self):
        url = self.PLAYLIST_URL
        headers = {
            'Authorization': 'Device %s' % self.DEVICE_ID
        }
        self.LOG.debug('Fetching remote playlist from %s' % url)
        try:
            response = requests.get(
                url,
                timeout=(None, 60),
                stream=False,
                headers=headers)
            if response.status_code == 200:

                self.LOG.debug('Feteched data: %s' % response.content)
                return response.content
            else:
                self.LOG.debug('Failed to fetch data with status: %s and content: %s',
                               response.status_code, response.content)
                return None
        except Exception, e:
            self.LOG.error('Could not fetch playlist %s, %s' % (url, e))
            return None

    def fetch_local_playlist_data(self):
        if os.path.isfile(self.PLAYLIST_FILEPATH):
            local_playlist = open(self.PLAYLIST_FILEPATH).read()
            if len(local_playlist) == 0:
                return None
            return local_playlist
        else:
            self.LOG.debug('No stored playlist')
            return None

    def fetch_playlist(self, **kwargs):
        if 'local' in kwargs and kwargs['local'] is True:
            pl_data = self.fetch_local_playlist_data()
            if pl_data is None:
                return self.playlist
        else:
            pl_data = self.fetch_remote_playlist_data()
            if pl_data is None:
                return self.playlist
            with open(self.PLAYLIST_FILEPATH, 'w') as pl_file:
                pl_file.write(pl_data)
            pl_file.close()

        # If raw playlist data was acquired, create a playlist
        try:
            playlist_dl = json.loads(pl_data)
        except Exception, e:
            self.LOG.error('Playlist likely corrupted: %s' % e)
            return self.playlist
        self.LOG.debug('Playlist fetched %s', playlist_dl)
        media_schedule = literal_eval(playlist_dl[PlaylistManager.SCHEDULE_NAME_STRING])
        media_schedule = self.generate_viewer_playlist(media_schedule)
        self.LOG.debug('Media schedule %s', media_schedule)
        # if this after playlist saved on disk
        self.download_playlist_files(media_schedule)
        self.playlist = media_schedule
        self.LOG.debug('Using playlist %s', self.playlist)
        return self.playlist

    def generate_viewer_playlist(self, playlist):
        viewer_pl = []
        for content in playlist:
            self.LOG.debug("Generating playlist for content: %s", content)
            content_type = content[PlaylistManager.SCHEDULE_TYPE_STRING]
            content_uri = content[PlaylistManager.SCHEDULE_URI_STRING]
            view_time = int(content[PlaylistManager.SCHEDULE_TIME_STRING])
            media = Media(content_type, content_uri, view_time)
            viewer_pl.append(media)
        return viewer_pl

    # NOTE: Also sets content_uri to local uri
    def download_playlist_files(self, playlist):
        playlist_changed = False
        for content in playlist:
            if content.content_type == 'web_page':
                continue  # Web pages are not downloaded
            out_file_path = self.generate_content_filepath(content.content_uri, content.content_type)
            self.LOG.debug(out_file_path)
            if os.path.isfile(out_file_path):
                self.LOG.debug("Found file %s", out_file_path)
                content.content_uri = out_file_path
                continue
            playlist_changed = True
            try:
                self.download_and_save_content(content.content_uri, out_file_path)
            except Exception, e:
                self.LOG.error('Failed to download content, %s %s', content, e)
                return False
            content.content_uri = out_file_path

        return playlist_changed

    def download_and_save_content(self, content_uri, out_file_path):
        resumable_dl = ResumableFileDownload(
            content_uri,
            out_file_path,
            self.downloader
        )
        resumable_dl.download()

    def generate_filename(self, content_uri, content_type):
        uri_split = content_uri.split('/')
        if len(uri_split) == 0:
            return str(hash(content_uri)) + '.' + content_type
        else:
            return uri_split[len(uri_split)-1]

    def generate_content_filepath(self, content_uri, content_type):
        file_name = self.generate_filename(content_uri, content_type)
        return self.MEDIA_FOLDER + file_name
