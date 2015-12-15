import ConfigParser
import os
import json
from playlist_manager import PlaylistJsonParser
import time
import logging

class MediaCleaner(object):
    '''
    Checks available disk space and removes unused media.
    '''
    LOG = logging.getLogger(__name__)

    def __init__(self, config):
        playlist_filepath = config.get('Storage', 'playlist_file')
        self.cleanup_time_h = config.get('Storage', 'cleanup_time_h')
        self.threshold_mb = config.get('Storage', 'cleanup_threshold_mb')
        self.media_folder = config.get('Storage', 'media_folder')
        self.playlist_parser = PlaylistJsonParser(
            self.media_folder,
            playlist_filepath
        )
        self.LOG.debug('Initialized %s' % __name__)

    def clean_media(self, force_clean_unused=False):
        self.LOG.debug('Cleaning up old media (force_clean_unused=%s)' % force_clean_unused)
        if self.is_cleanup_required():
            force_clean_unused = True
        unused_media = self.get_all_currently_unused_media()
        for media in unused_media:
            if force_clean_unused or self.is_media_old(media):
                self.LOG.debug('Removing old media: %s' % media)
                os.remove(media)

    def is_force_cleanup_required(self):
        statvfs = os.statvfs(self.media_folder)
        free_blocks = statvfs.f_bavail
        block_size = statvfs.f_frsize
        free_bytes = free_blocks* block_size
        free_megs = free_bytes / 1000000
        cleanup_required = free_megs <= self.threshold_mb
        self.LOG.debug(
            'Free megabytes: %s, cleanup_threshold_mb: %s, cleanup required: %s' %
            (free_megs, self.threshold_mb, cleanup_required)
        )
        return cleanup_required

    def is_media_old(self, media_filepath):
        stat = os.stat(media_filepath)
        media_age_h = ((time.time() - stat.st_mtime) / 3600)
        self.LOG.debug('Age of %s: %s' % (media_filepath, media_age_h))
        return media_age_h >= self.cleanup_time_h

    def get_all_currently_unused_media(self):
        current_media_files = []
        stored_playlist = self.playlist_parser.get_stored_playlist()
        if stored_playlist is None:
            return []
        for media in stored_playlist:
            if media.content_type == 'web_page':
                continue
            media_filepath = self.playlist_parser.get_storage_filepath_for_media(media)
            current_media_files.append(media_filepath)
        all_files = [os.path.join(self.media_folder, file) for file in os.listdir(self.media_folder)]
        unused_files = []
        for file in all_files:
            file = file.encode('UTF-8')
            if not file in current_media_files:
                unused_files.append(file)
        self.LOG.debug('Found unused media files: %s' % unused_files)
        return unused_files


if __name__ == '__main__':
    START_PATH = os.path.dirname(os.path.realpath(__file__))
    CONFIG_PATH = os.path.join(START_PATH, 'client.properties')
    config = ConfigParser.ConfigParser()
    with open(CONFIG_PATH) as config_fp:
        config.readfp(config_fp)
    cleaner = MediaCleaner(config)
    cleaner.clean_media(True)
