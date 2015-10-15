import logging
logging.basicConfig(filename='demo_client.log', filemode='w', level=logging.DEBUG)
import ConfigParser
import urllib2
import json
import sys
from ast import literal_eval
import time
import os
from display.media import Media
from display.scheduler import Scheduler

class Client(object):
    
    SCHEDULE_NAME_STRING = 'media_schedule_json';
    SCHEDULE_TIME_STRING  = 'time';
    SCHEDULE_TYPE_STRING  = 'type';
    SCHEDULE_URI_STRING = 'uri';
    
    def __init__(self, config_path):
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(config_path))
        self.scheduler = None
        self.playlist = None
        logging.debug('Initiating client with config: %s', config_path)

    def fetch_playlist(self):
        url = self.config.get('Server', 'playlist_url')
        logging.debug('Fetching playlist from url %s', url)
        try:
            response = urllib2.urlopen(url).read()
        except Exception, e:
            logging.error('Could not fetch playlist %s', e)
            return
        playlist_dl = json.loads(response)
        logging.debug('Playlist fetched %s', playlist_dl)
        media_schedule = literal_eval(playlist_dl[Client.SCHEDULE_NAME_STRING])
        media_schedule = self.generate_viewer_playlist(media_schedule)
        logging.debug('Media schedule %s', media_schedule)
        #if this after playlist saved on disk
        self.download_playlist_files(media_schedule)
        self.playlist = media_schedule
        logging.debug('Using playlist %s', self.playlist)

    def generate_viewer_playlist(self, playlist):
        viewer_pl = []
        for content in playlist:
            logging.debug("Generating playlist for content: %s", content);
            content_type = content[Client.SCHEDULE_TYPE_STRING]
            content_uri = content[Client.SCHEDULE_URI_STRING]
            view_time = int(content[Client.SCHEDULE_TIME_STRING])
            m = Media(content_type, content_uri, view_time)
            viewer_pl.append(m)
        return viewer_pl

# NOTE: Also sets content_uri to local uri
    def download_playlist_files(self, playlist):
        media_folder = self.config.get('Storage', 'media_folder')
        playlist_changed = False;
        for content in playlist:
            out_file_path = self.generate_content_filepath(content.content_uri)
            logging.debug(out_file_path)
            if os.path.isfile(out_file_path):
                logging.debug("Found file %s", out_file_path)
                content.content_uri = out_file_path
                continue;
            playlist_changed = True;
            try:
                logging.debug("Downloading content: %s", content);
                downloaded_data = self.download_content(content.content_uri)
                logging.debug("downloaded_data %s", downloaded_data)
            except Exception, e:
                logging.error('Failed to download content, %s %s', content, e)
                return False;
            try:
                content_file = open(out_file_path, 'w+')
                content_file.write(downloaded_data)
            except IOError, e:
                logging.error('Failed to save content , %s %s', content, e)
                return False;
            content.content_uri = out_file_path
            
        return playlist_changed;

    def download_content(self, content_uri):
        logging.debug("download_content() %s", content_uri)
        return urllib2.urlopen(content_uri).read()

    def generate_content_filepath(self, content_uri):
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
        
        if not self.scheduler.running:
            self.scheduler.start()


    def poll_playlist(self):
        try:
            while True:
                self.fetch_playlist()
                self.schedule_playlist()
                poll_time = float(self.config.get('Client', 'playlist_poll_time'))
                time.sleep(poll_time)
        except KeyboardInterrupt, e:
            if self.scheduler:
                self.scheduler.shutdown()
                                