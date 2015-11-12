'''
A high-level class for viewing any supported media type.
Delegates viewing to the browser or video player depending on media
type. The displaying is performed in a separate thread, so shutdown()
must be called before killing the program to avoid errors upon
program termination.
'''

import time
import logging
from media import Media
from browser import Browser
from video_player import VideoPlayer


class Viewer(object):

    DISPLAY_TIME_GRANULARITY = 1  # seconds
    BROWSER = Browser()
    PLAYER = VideoPlayer()

    VIEWERS = {
        Media.IMAGE: BROWSER,
        Media.WEB_PAGE: BROWSER,
        Media.VIDEO: PLAYER
    }
    previous_content_type = None
    viewer = None

    def display_content(self, content):
        if self.viewer is not None and content.content_type != self.previous_content_type:
            self.viewer.hide()
        logging.debug('Viewer received content %s', content)
        self.viewer = self.VIEWERS[content.content_type]

        displayed_time = 0
        self.viewer.display_content(content)
        self.running = True

        while self.running and displayed_time < content.view_time:
            time.sleep(self.DISPLAY_TIME_GRANULARITY)
            displayed_time += self.DISPLAY_TIME_GRANULARITY
            self.keep_alive(self.viewer, content)

        self.previous_content_type = content.content_type
        logging.debug('Viewer finished displaying content %s', content)

    def keep_alive(self, viewer, content):
        if not viewer.is_alive():
            logging.debug('Resurrecting viewer for content %s', content)
            viewer.display_content(content)

    def shutdown(self):
        logging.debug('Viewer shutdown requested')
        self.running = False
        self.BROWSER.shutdown()
        self.PLAYER.shutdown()
        logging.debug('Viewer shutdown complete')
