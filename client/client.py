import ConfigParser
import urllib2
import json
from ast import literal_eval
import time
import os
from display.media import Media
from display.scheduler import Scheduler
import logging

class Client(object):

    SCHEDULE_NAME_STRING = 'media_schedule_json'
    SCHEDULE_TIME_STRING = 'time'
    SCHEDULE_TYPE_STRING = 'type'
    SCHEDULE_URI_STRING = 'uri'

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.MEDIA_FOLDER = self.config.get('Storage', 'media_folder')
        if self.MEDIA_FOLDER[len(self.MEDIA_FOLDER)-1] != '/':
            self.MEDIA_FOLDER += '/'
        if not os.path.exists(self.MEDIA_FOLDER):
            os.makedirs(self.MEDIA_FOLDER)

        playlist_file = self.config.get('Storage', 'playlist_file')
        playlist_folder = os.path.dirname(playlist_file);
        if not os.path.exists(playlist_folder):
            os.makedirs(playlist_folder)
        self.PLAYLIST_FILEPATH = playlist_file

        self.scheduler = None
        self.playlist = None
        # Get the device id and format the playlist url to use it
        device_id_file = open(self.config.get('Device', 'device_id_file'), 'r')
        self.device_id = device_id_file.read().strip()
        device_id_file.close()
        incomplete_url = self.config.get('Server', 'playlist_url')
        playlist_url = incomplete_url.format(**{'device_id': self.device_id})
        self.config.set('Server', 'playlist_url', playlist_url)
        self.logger.debug('Initiating client with config: %s', config)

    def fetch_playlist(self):
        url = self.config.get('Server', 'playlist_url')
        self.logger.debug('Fetching playlist from url %s', url)
        download_success = True
        try:
            pl_data = urllib2.urlopen(url).read()
        except Exception, e:
            self.logger.error('Could not fetch playlist %s, using stored playlist', e)
            download_success = False
            if os.path.isfile(self.PLAYLIST_FILEPATH):
                pl_data = open(self.PLAYLIST_FILEPATH).read()
            else:
                self.logger.debug('No stored playlist, setting empty playlist')
                self.playlist = []
                return
        if download_success:
            pl_file = open(self.PLAYLIST_FILEPATH, 'w+')
            pl_file.write(pl_data)
            pl_file.close()
        playlist_dl = json.loads(pl_data)
        self.logger.debug('Playlist fetched %s', playlist_dl)
        media_schedule = literal_eval(playlist_dl[Client.SCHEDULE_NAME_STRING])
        media_schedule = self.generate_viewer_playlist(media_schedule)
        self.logger.debug('Media schedule %s', media_schedule)
        # if this after playlist saved on disk
        self.download_playlist_files(media_schedule)
        self.playlist = media_schedule
        self.logger.debug('Using playlist %s', self.playlist)

    def generate_viewer_playlist(self, playlist):
        viewer_pl = []
        for content in playlist:
            self.logger.debug("Generating playlist for content: %s", content)
            content_type = content[Client.SCHEDULE_TYPE_STRING]
            content_uri = content[Client.SCHEDULE_URI_STRING]
            view_time = int(content[Client.SCHEDULE_TIME_STRING])
            m = Media(content_type, content_uri, view_time)
            viewer_pl.append(m)
        return viewer_pl

    # NOTE: Also sets content_uri to local uri
    def download_playlist_files(self, playlist):
        playlist_changed = False
        for content in playlist:
            out_file_path = self.generate_content_filepath(content.content_uri)
            self.logger.debug(out_file_path)
            if os.path.isfile(out_file_path):
                self.logger.debug("Found file %s", out_file_path)
                content.content_uri = out_file_path
                continue
            playlist_changed = True
            try:
                self.logger.debug("Downloading content: %s", content)
                self.download_and_save_content(content.content_uri, out_file_path)
                self.logger.debug("downloaded_data")
            except Exception, e:
                self.logger.error('Failed to download content, %s %s', content, e)
                return False
            content.content_uri = out_file_path

        return playlist_changed

    def download_and_save_content(self, content_uri, out_file_path):
        content_uri = self.append_device_id_to_url(content_uri)
        self.logger.debug("download_content() %s", content_uri)
        response = urllib2.urlopen(content_uri)
        with open(out_file_path, 'wb') as out_file:
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                out_file.write(chunk)

    def append_device_id_to_url(self, url):
        device_id_query_param = '?device_id=%s' % self.device_id
        return url + device_id_query_param

    def generate_content_filepath(self, content_uri):
        uri_split = content_uri.split('.')
        file_extension = uri_split[len(uri_split) - 1]
        file_name = str(hash(content_uri))
        return self.MEDIA_FOLDER + file_name + '.' + file_extension

    def schedule_playlist(self):
        if self.playlist is None or len(self.playlist) == 0:
            self.logger.debug('No playlist to schedule')
            return

        if self.scheduler is None:
            self.scheduler = Scheduler()

        def replace_playlist(scheduled_pl):
            del scheduled_pl[:]
            for media in self.playlist:
                scheduled_pl.append(media)
        self.scheduler.modify_playlist_atomically(replace_playlist)

        if not self.scheduler.running:
            self.scheduler.start()

    def poll_playlist(self):
        poll_time = float(self.config.get('Client', 'playlist_poll_time'))
        try:
            while True:
                self.fetch_playlist()
                self.schedule_playlist()
                time.sleep(poll_time)
        except KeyboardInterrupt:
            if self.scheduler:
                self.scheduler.shutdown()
