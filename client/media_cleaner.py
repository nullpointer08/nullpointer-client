import logging
import os
from stat import ST_ATIME
from display.media import Media
import playlist_utils
from settings import MEDIA_FOLDER, CLEANUP_THRESHOLD_BYTES, EXTRA_SPACE_TO_FREE_UP_BYTES


class MediaCleaner(object):
    """
    Checks available disk space and if there's not enough disk space to download a file it removes unused media.
    """
    LOG = logging.getLogger(__name__)

    def __init__(self):
        self.LOG.debug('Initialized %s' % __name__)

    def enough_space(self, content_length):
        statvfs = os.statvfs(MEDIA_FOLDER)
        free_blocks = statvfs.f_bavail
        block_size = statvfs.f_frsize
        free_bytes = free_blocks * block_size
        self.LOG.debug('Free space in bytes: %s', free_bytes)
        self.LOG.debug('Content_length: %s and cleanup threshold: %s',
                       content_length, CLEANUP_THRESHOLD_BYTES)
        if free_bytes < (content_length + CLEANUP_THRESHOLD_BYTES):
            return False
        return True

    def clean_media(self, content_length):
        if not self.enough_space(content_length):
            self.run_cleanup(content_length)

    def run_cleanup(self, content_length):
        self.LOG.debug('Cleaning up old media.')
        unused_media = self.get_all_currently_unused_media()

        for media in unused_media:
            if self.enough_space(content_length + EXTRA_SPACE_TO_FREE_UP_BYTES):
                break
            self.LOG.debug('Removing old media: %s', media[1])
            os.remove(media[1])

        if not self.enough_space(content_length):
            raise Exception("Could not free up enough space")

    def get_all_currently_unused_media(self):
        current_media_files = []
        stored_playlist = playlist_utils.get_stored_playlist()
        if stored_playlist and len(stored_playlist):
            for media in stored_playlist:
                if media.content_type == Media.WEB_PAGE:
                    continue
                media_filepath = media.content_uri
                current_media_files.append(media_filepath)
        all_files = [os.path.join(MEDIA_FOLDER, file) for file in os.listdir(MEDIA_FOLDER)]
        unused_files = []
        for file in all_files:
            file = file.encode('UTF-8')
            if not file in current_media_files:
                pair = (os.stat(file)[ST_ATIME], file)
                unused_files.append(pair)

        unused_files = sorted(unused_files)

        self.LOG.debug('Found unused media files: %s' % unused_files)
        return unused_files