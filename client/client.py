import logging
logging.basicConfig(filename='demo_client.log', filemode='w', level=logging.DEBUG)

import ConfigParser
import urllib2
import json
import sys
import time
import os
from display.media import Media
from display.scheduler import Scheduler

class Client(object):

    def __init__(self, config_path):
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(config_path))
        self.scheduler = None
        self.playlist = None
        logging.info('Initiating client with config: %s', config_path)

    def fetch_playlist(self):
        url = self.config.get('Server', 'playlist_url')
        logging.debug('Fetching playlist from url %s', url)

        try:
            response = urllib2.urlopen(url).read()
        except Exception, e:
            logging.error('Could not fetch playlist %s', e)
            return

        playlist_dl = json.loads(response)
        self.download_playlist_files(playlist_dl)
        self.playlist = self.generate_viewer_playlist(playlist_dl)
        logging.info('Using playlist %s', self.playlist)

    def generate_viewer_playlist(self, playlist):
        viewer_pl = []
        for content in playlist:
            content_type = content['content_type']
            content_uri = self.generate_content_filepath(content)
            view_time = int(content['view_time'])
            m = Media(content_type, content_uri, view_time)
            viewer_pl.append(m)
        return viewer_pl

    def download_playlist_files(self, playlist):
        media_folder = self.config.get('Storage', 'media_folder')
        for content in playlist:
            out_file_path = self.generate_content_filepath(content)
            if os.path.isfile(out_file_path):
                continue

            try:
                downloaded_data = self.download_content(content)
            except Exception, e:
                logging.error('Failed to download content, %s %s', content, e)
                continue

            content_file = open(out_file_path, 'w+')
            content_file.write(downloaded_data)

    def download_content(self, content):
        content_uri = content['content_uri']
        return urllib2.urlopen(content_uri).read()

    def generate_content_filepath(self, content):
        content_uri = content['content_uri']
        uri_split = content_uri.split('.')
        file_extension = uri_split[len(uri_split) - 1]
        file_name = str(hash(content_uri))
        media_folder = self.config.get('Storage', 'media_folder')
        return media_folder + file_name + '.' + file_extension


    def schedule_playlist(self):
        if self.playlist is None or len(self.playlist) == 0:
            logging.debug('No playlist to schedule')
            return

        if self.scheduler is None:
            self.scheduler = Scheduler()
        def replace_playlist(scheduled_pl):
            del scheduled_pl[:]
            for media in self.playlist:
                scheduled_pl.append(media)
        self.scheduler.modify_playlist_atomically(replace_playlist)
        self.scheduler.start()


    def poll_playlist(self):
        while True:
            self.fetch_playlist()
            self.schedule_playlist()
            poll_time = float(self.config.get('Client', 'playlist_poll_time'))
            time.sleep(poll_time)

