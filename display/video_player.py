'''
A control class for the video player.
'''

import sh
import logging
from media import Media

class VideoPlayer(object):
    
    def __init__(self):
        logging.debug('Initializing VideoPlayer')
        self.process = None

    def display_content(self, content):
        assert content.content_type == Media.VIDEO
        logging.debug('VideoPlayer receiving content %s', content)
        uri = content.content_uri
        self.process = sh.omxplayer('--loop', '--no-osd', uri, _bg=True)

    # Cannot really hide player, must shut down
    def hide(self):
        logging.debug('VideoPlayer hide called')
        self.shutdown()

    def shutdown(self):
        logging.debug('VideoPlayer shutdown called')
        if self.is_alive():
            self.process.process.stdin.put('q')

    def is_alive(self):
        return self.process is not None and self.process.process.alive
