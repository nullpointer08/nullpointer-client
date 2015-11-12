'''
A control class for the video player.
'''

import sh
import logging
import platform
from media import Media


class VideoPlayer(object):

    def __init__(self):
        logging.debug('Initializing VideoPlayer')
        self.process = None

    def display_content(self, content):
        assert content.content_type == Media.VIDEO
        logging.debug('VideoPlayer receiving content %s', content)
        uri = content.content_uri
        if(platform.linux_distribution()[0] == "Ubuntu"):
            self.process = sh.vlc(
                '--no-osd', '-f', '--no-interact', '--repeat',
                '--mouse-hide-timeout', '--no-video-title-show',
                '--video-on-top', uri, _bg=True
            )
        else:
            self.process = sh.omxplayer(
                '--no-osd', '-b', '--loop', uri, _bg=True)

    # Cannot really hide player, must shut down
    def hide(self):
        logging.debug('VideoPlayer hide called')
        self.shutdown()

    def shutdown(self):
        logging.debug('VideoPlayer shutdown called')
        if self.is_alive():
            if platform.linux_distribution()[0] == "Ubuntu":
                sh.pkill('vlc')
            else:
                sh.killall('omxplayer.bin', _ok_code=[0,1])

    def is_alive(self):
        if self.process is None:
            return False
        else:
            return self.process.process.exit_code is None


def print_std(line):
    print str(line)
