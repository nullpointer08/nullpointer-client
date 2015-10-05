'''
A control class for the video player.
'''

import sh
from media import Media

class VideoPlayer(object):
    
    def __init__(self):
        self.process = None

    def display_content(self, content):
        assert content.content_type == Media.VIDEO
        uri = content.content_uri
        self.process = sh.omxplayer('--loop', '--no-osd', uri, _bg=True)

    # Cannot really hide player, must shut down
    def hide(self):
        print "Hide video player"
        self.shutdown()

    def shutdown(self):
        if self.is_alive():
            self.process.process.stdin.put('q')

    def is_alive(self):
        return self.process is not None and self.process.process.alive
